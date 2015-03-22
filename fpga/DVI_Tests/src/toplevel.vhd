library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.video_bus.all;
use work.ram_port.all;
use work.camera_pkg.all;
use work.simple_mac_pkg.all;
use work.util_arbiter_pkg.all;


entity toplevel is
    port (
        -- Clock, Reset
        clk_100MHz : in std_logic;
        rst_n : in std_logic;
        
        -- DVI Interface
        tx_tmds : out std_logic_vector(3 downto 0);
        tx_tmdsb : out std_logic_vector(3 downto 0);
        rx_tmds : in std_logic_vector(3 downto 0);
        rx_tmdsb : in std_logic_vector(3 downto 0);
        rx_sda : inout std_logic;
        rx_scl : inout std_logic;
        
        led : out std_logic_vector(7 downto 0);
        BTNU, BTNL, BTND, BTNR, BTNC : in std_logic;

        -- Camera interfaces
        left_camera_out  : out camera_out;
        left_camera_in   : in  camera_in;
        right_camera_out : out camera_out;
        right_camera_in  : in  camera_in;
        
        pair7P:  inout std_logic;
        pair7N:  inout std_logic;
        pair8P:  inout std_logic;
        pair8N:  inout std_logic;
        pair9P:  inout std_logic;
        pair9N:  inout std_logic;
        pair12P: inout std_logic;
        pair12N: inout std_logic;
        pair13P: inout std_logic;
        pair13N: inout std_logic;
        pair14P: inout std_logic;
        pair14N: inout std_logic;

        uart_tx : out std_logic;
        uart_rx : in std_logic;

        -- DDR2 Interface
        mcb3_dram_dq     : inout  std_logic_vector(16-1 downto 0);
        mcb3_dram_a      : out std_logic_vector(13-1 downto 0);
        mcb3_dram_ba     : out std_logic_vector(3-1 downto 0);
        mcb3_dram_ras_n  : out std_logic;
        mcb3_dram_cas_n  : out std_logic;
        mcb3_dram_we_n   : out std_logic;
        mcb3_dram_odt    : out std_logic;
        mcb3_dram_cke    : out std_logic;
        mcb3_dram_dm     : out std_logic;
        mcb3_dram_udqs   : inout  std_logic;
        mcb3_dram_udqs_n : inout  std_logic;
        mcb3_rzq         : inout  std_logic;
        mcb3_zio         : inout  std_logic;
        mcb3_dram_udm    : out std_logic;
        mcb3_dram_dqs    : inout  std_logic;
        mcb3_dram_dqs_n  : inout  std_logic;
        mcb3_dram_ck     : out std_logic;
        mcb3_dram_ck_n   : out std_logic;
        
        -- Ethernet PHY
        phyrst           : out   std_logic;
        phytxclk         : in    std_logic;
        phyTXD           : out   std_logic_vector(7 downto 0);
        phytxen          : out   std_logic;
        phytxer          : out   std_logic;
        phygtxclk        : out   std_logic;
        phyRXD           : in    std_logic_vector(7 downto 0);
        phyrxdv          : in    std_logic;
        phyrxer          : in    std_logic;
        phyrxclk         : in    std_logic;
        phymdc           : out   std_logic;
        phymdi           : inout std_logic;
        phyint           : in    std_logic; -- currently unused
        phycrs           : in    std_logic;
        phycol           : in    std_logic);
end entity toplevel;


architecture RTL of toplevel is
    signal reset             : std_logic;
    signal clk_100MHz_buf    : std_logic;
    signal clk_camera_unbuf  : std_logic;
    signal clk_camera_over_2 : std_logic;
    signal clk_camera_over_5 : std_logic;
    signal clk_pixel         : std_logic;
    signal clk_ethernet      : std_logic;
    signal clk_locked        : std_logic;
    
    constant SPI_ARBITER_USERS : natural := 3;
    
    signal spi_arbiter_users_in  : ArbiterUserInArray (0 to SPI_ARBITER_USERS-1);
    signal spi_arbiter_users_out : ArbiterUserOutArray(0 to SPI_ARBITER_USERS-1);
    
    signal SCLK : std_logic;

    -- DDR2 Signals
    signal c3_calib_done : std_logic;
    signal c3_clk0       : std_logic;
    signal c3_rst0       : std_logic;

    signal c3_p0_in  : ram_bidir_port_in;
    signal c3_p0_out : ram_bidir_port_out;

    signal c3_p1_in         : ram_bidir_port_in;
    signal c3_p1_out        : ram_bidir_port_out;
    signal c3_p1_rdonly_in  : ram_rd_port_in;
    signal c3_p1_rdonly_out : ram_rd_port_out;
    signal c3_p1_wronly_in  : ram_wr_port_in;
    signal c3_p1_wronly_out : ram_wr_port_out;

    signal c3_p2_in  : ram_rd_port_in;
    signal c3_p2_out : ram_rd_port_out;

    signal c3_p3_in  : ram_rd_port_in;
    signal c3_p3_out : ram_rd_port_out;

    signal c3_p4_in  : ram_rd_port_in;
    signal c3_p4_out : ram_rd_port_out;

    signal c3_p5_in  : ram_wr_port_in;
    signal c3_p5_out : ram_wr_port_out;
    
    signal reset_for_ram_user : std_logic;


    signal dummy_video : video_bus;
    signal received_video : video_bus;
    signal overlay_video : video_bus;
    signal base_video_data : video_data;
    signal composite_video : video_bus;


    signal uart_tx_ready : std_logic;
    signal uart_tx_data : std_logic_vector(7 downto 0);
    signal uart_tx_write : std_logic;

    signal uart_rx_valid : std_logic;
    signal uart_rx_data : std_logic_vector(7 downto 0);
    
    constant                LEFT_CAMERA_MEMORY_LOCATION : integer :=  0*1024*1024;
    constant               RIGHT_CAMERA_MEMORY_LOCATION : integer := 32*1024*1024;
    constant DISTORTER_PREFETCHER_TABLE_MEMORY_LOCATION : integer := 64*1024*1024;
    constant              DISTORTER_MAP_MEMORY_LOCATION : integer := 96*1024*1024;
    
    signal phy_in  : PHYInInterface;
    signal phy_out : PHYOutInterface;
begin
    reset <= not rst_n;

    IBUFG_inst : IBUFG
        port map(
            O => clk_100MHz_buf, -- Clock buffer output
            I => clk_100MHz      -- Clock buffer input (connect directly to top-level port)
        );

    U_PIXEL_CLK_GEN : entity work.pixel_clk_gen port map (
        CLK_IN_100MHz         => clk_100MHz_buf,
        CLK_OUT_CAMERA_UNBUF  => clk_camera_unbuf,
        CLK_OUT_CAMERA_OVER_2 => clk_camera_over_2,
        CLK_OUT_CAMERA_OVER_5 => clk_camera_over_5,
        CLK_OUT_PIXEL         => clk_pixel,
        CLK_OUT_ETHERNET      => clk_ethernet,
        RESET                 => '0',
        LOCKED                => clk_locked);
    
    U_SPI_ARBITER : entity work.util_arbiter
        generic map (
            USERS => SPI_ARBITER_USERS)
        port map (
            clock => clk_100MHz_buf,
            users_in => spi_arbiter_users_in,
            users_out => spi_arbiter_users_out);

    U_LEFT_CAMERA : entity work.camera -- C2
        generic map (
            CLOCK_FREQUENCY => 100.0E6,
            
            CPLD_CONFIG_BASE => 0,
            
            SYNC_INVERTED   => false,
            DATA3_INVERTED  => false,
            DATA2_INVERTED  => true,
            DATA1_INVERTED  => false,
            DATA0_INVERTED  => false,
            MEMORY_LOCATION => LEFT_CAMERA_MEMORY_LOCATION)
        port map (
            clock               => clk_100MHz_buf,
            clock_camera_unbuf  => clk_camera_unbuf,
            clock_camera_over_2 => clk_camera_over_2,
            clock_camera_over_5 => clk_camera_over_5,
            clock_locked        => clk_locked,
            reset               => reset,
            
            camera_out => left_camera_out,
            camera_in  => left_camera_in,
            
            MISO => pair8P,
            MOSI => pair14N,
            SCLK => SCLK,
            nSS  => pair7P,
            
            cpld_MOSI => pair14N,
            cpld_MISO => pair13N,
            cpld_SCLK => SCLK,
            cpld_nSS  => pair14P,
            
            spi_arbiter_in => spi_arbiter_users_in(2),
            spi_arbiter_out => spi_arbiter_users_out(2),
            
            ram_in  => c3_p1_wronly_in,
            ram_out => c3_p1_wronly_out);
    
    U_RIGHT_CAMERA : entity work.camera -- C1
        generic map (
            CLOCK_FREQUENCY => 100.0E6,
            
            CPLD_CONFIG_BASE => 4,
            
            SYNC_INVERTED   => true,
            DATA3_INVERTED  => true,
            DATA2_INVERTED  => true,
            DATA1_INVERTED  => false,
            DATA0_INVERTED  => false,
            MEMORY_LOCATION => RIGHT_CAMERA_MEMORY_LOCATION)
        port map (
            clock               => clk_100MHz_buf,
            clock_camera_unbuf  => clk_camera_unbuf,
            clock_camera_over_2 => clk_camera_over_2,
            clock_camera_over_5 => clk_camera_over_5,
            clock_locked        => clk_locked,
            reset               => reset,
            
            camera_out => right_camera_out,
            camera_in  => right_camera_in,
            
            MISO => pair8N,
            MOSI => pair14N,
            SCLK => SCLK,
            nSS  => pair7N,
            
            cpld_MOSI => pair14N,
            cpld_MISO => pair13N,
            cpld_SCLK => SCLK,
            cpld_nSS  => pair14P,
            
            spi_arbiter_in => spi_arbiter_users_in(1),
            spi_arbiter_out => spi_arbiter_users_out(1),
            
            ram_in  => c3_p5_in,
            ram_out => c3_p5_out);
    
    process (clk_100MHz_buf) is
        variable SCLK_1, SCLK_2 : std_logic;
        constant DELAY : positive := 25;
        variable countdown : integer range 0 to 2*DELAY := 0;
        variable last_SCLK : std_logic;
        variable last_SCLK_set : boolean := false;
    begin
        if rising_edge(clk_100MHz_buf) then
            if countdown /= 0 then
                if countdown = DELAY then
                    pair12P <= '0';
                    pair13P <= '0';
                end if;
                countdown := countdown - 1;
            elsif not last_SCLK_set or SCLK_2 /= last_SCLK then
                if SCLK_2 = '1' then
                    pair12P <= '1';
                else
                    pair13P <= '1';
                end if;
                countdown := 2*DELAY;
                last_SCLK := SCLK_2;
                last_SCLK_set := true;
            end if;
            SCLK_2 := SCLK_1;
            SCLK_1 := SCLK;
        end if;
    end process;
    
    --SCLK <= 'H';
    --pair7N <= 'H';
    --pair7P <= 'H';
    
    --------------------------
    -- DDR2 Interface
    --------------------------

    u_dram : entity work.dram port map (
        c3_sys_clk          => clk_100MHz_buf,
        c3_sys_rst_i        => reset,
        mcb3_dram_dq        => mcb3_dram_dq,
        mcb3_dram_a         => mcb3_dram_a,
        mcb3_dram_ba        => mcb3_dram_ba,
        mcb3_dram_ras_n     => mcb3_dram_ras_n,
        mcb3_dram_cas_n     => mcb3_dram_cas_n,
        mcb3_dram_we_n      => mcb3_dram_we_n,
        mcb3_dram_odt       => mcb3_dram_odt,
        mcb3_dram_cke       => mcb3_dram_cke,
        mcb3_dram_ck        => mcb3_dram_ck,
        mcb3_dram_ck_n      => mcb3_dram_ck_n,
        mcb3_dram_dqs       => mcb3_dram_dqs,
        mcb3_dram_dqs_n     => mcb3_dram_dqs_n,
        mcb3_dram_udqs      => mcb3_dram_udqs,    -- for X16 parts
        mcb3_dram_udqs_n    => mcb3_dram_udqs_n,  -- for X16 parts
        mcb3_dram_udm       => mcb3_dram_udm,     -- for X16 parts
        mcb3_dram_dm        => mcb3_dram_dm,
        c3_clk0             => c3_clk0,
        c3_rst0             => c3_rst0,
        c3_calib_done       => c3_calib_done,
        mcb3_rzq            => mcb3_rzq,
        mcb3_zio            => mcb3_zio,

        c3_p0_cmd_clk       => c3_p0_in.cmd.clk,
        c3_p0_cmd_en        => c3_p0_in.cmd.en,
        c3_p0_cmd_instr     => c3_p0_in.cmd.instr,
        c3_p0_cmd_bl        => c3_p0_in.cmd.bl,
        c3_p0_cmd_byte_addr => c3_p0_in.cmd.byte_addr,
        c3_p0_cmd_empty     => c3_p0_out.cmd.empty,
        c3_p0_cmd_full      => c3_p0_out.cmd.full,
        c3_p0_wr_clk        => c3_p0_in.wr.clk,
        c3_p0_wr_en         => c3_p0_in.wr.en,
        c3_p0_wr_mask       => c3_p0_in.wr.mask,
        c3_p0_wr_data       => c3_p0_in.wr.data,
        c3_p0_wr_full       => c3_p0_out.wr.full,
        c3_p0_wr_empty      => c3_p0_out.wr.empty,
        c3_p0_wr_count      => c3_p0_out.wr.count,
        c3_p0_wr_underrun   => c3_p0_out.wr.underrun,
        c3_p0_wr_error      => c3_p0_out.wr.error,
        c3_p0_rd_clk        => c3_p0_in.rd.clk,
        c3_p0_rd_en         => c3_p0_in.rd.en,
        c3_p0_rd_data       => c3_p0_out.rd.data,
        c3_p0_rd_full       => c3_p0_out.rd.full,
        c3_p0_rd_empty      => c3_p0_out.rd.empty,
        c3_p0_rd_count      => c3_p0_out.rd.count,
        c3_p0_rd_overflow   => c3_p0_out.rd.overflow,
        c3_p0_rd_error      => c3_p0_out.rd.error,

        c3_p1_cmd_clk       => c3_p1_in.cmd.clk,
        c3_p1_cmd_en        => c3_p1_in.cmd.en,
        c3_p1_cmd_instr     => c3_p1_in.cmd.instr,
        c3_p1_cmd_bl        => c3_p1_in.cmd.bl,
        c3_p1_cmd_byte_addr => c3_p1_in.cmd.byte_addr,
        c3_p1_cmd_empty     => c3_p1_out.cmd.empty,
        c3_p1_cmd_full      => c3_p1_out.cmd.full,
        c3_p1_wr_clk        => c3_p1_in.wr.clk,
        c3_p1_wr_en         => c3_p1_in.wr.en,
        c3_p1_wr_mask       => c3_p1_in.wr.mask,
        c3_p1_wr_data       => c3_p1_in.wr.data,
        c3_p1_wr_full       => c3_p1_out.wr.full,
        c3_p1_wr_empty      => c3_p1_out.wr.empty,
        c3_p1_wr_count      => c3_p1_out.wr.count,
        c3_p1_wr_underrun   => c3_p1_out.wr.underrun,
        c3_p1_wr_error      => c3_p1_out.wr.error,
        c3_p1_rd_clk        => c3_p1_in.rd.clk,
        c3_p1_rd_en         => c3_p1_in.rd.en,
        c3_p1_rd_data       => c3_p1_out.rd.data,
        c3_p1_rd_full       => c3_p1_out.rd.full,
        c3_p1_rd_empty      => c3_p1_out.rd.empty,
        c3_p1_rd_count      => c3_p1_out.rd.count,
        c3_p1_rd_overflow   => c3_p1_out.rd.overflow,
        c3_p1_rd_error      => c3_p1_out.rd.error,

        c3_p2_cmd_clk       => c3_p2_in.cmd.clk,
        c3_p2_cmd_en        => c3_p2_in.cmd.en,
        c3_p2_cmd_instr     => c3_p2_in.cmd.instr,
        c3_p2_cmd_bl        => c3_p2_in.cmd.bl,
        c3_p2_cmd_byte_addr => c3_p2_in.cmd.byte_addr,
        c3_p2_cmd_empty     => c3_p2_out.cmd.empty,
        c3_p2_cmd_full      => c3_p2_out.cmd.full,
        c3_p2_rd_clk        => c3_p2_in.rd.clk,
        c3_p2_rd_en         => c3_p2_in.rd.en,
        c3_p2_rd_data       => c3_p2_out.rd.data,
        c3_p2_rd_full       => c3_p2_out.rd.full,
        c3_p2_rd_empty      => c3_p2_out.rd.empty,
        c3_p2_rd_count      => c3_p2_out.rd.count,
        c3_p2_rd_overflow   => c3_p2_out.rd.overflow,
        c3_p2_rd_error      => c3_p2_out.rd.error,

        c3_p3_cmd_clk       => c3_p3_in.cmd.clk,
        c3_p3_cmd_en        => c3_p3_in.cmd.en,
        c3_p3_cmd_instr     => c3_p3_in.cmd.instr,
        c3_p3_cmd_bl        => c3_p3_in.cmd.bl,
        c3_p3_cmd_byte_addr => c3_p3_in.cmd.byte_addr,
        c3_p3_cmd_empty     => c3_p3_out.cmd.empty,
        c3_p3_cmd_full      => c3_p3_out.cmd.full,
        c3_p3_rd_clk        => c3_p3_in.rd.clk,
        c3_p3_rd_en         => c3_p3_in.rd.en,
        c3_p3_rd_data       => c3_p3_out.rd.data,
        c3_p3_rd_full       => c3_p3_out.rd.full,
        c3_p3_rd_empty      => c3_p3_out.rd.empty,
        c3_p3_rd_count      => c3_p3_out.rd.count,
        c3_p3_rd_overflow   => c3_p3_out.rd.overflow,
        c3_p3_rd_error      => c3_p3_out.rd.error,

        c3_p4_cmd_clk       => c3_p4_in.cmd.clk,
        c3_p4_cmd_en        => c3_p4_in.cmd.en,
        c3_p4_cmd_instr     => c3_p4_in.cmd.instr,
        c3_p4_cmd_bl        => c3_p4_in.cmd.bl,
        c3_p4_cmd_byte_addr => c3_p4_in.cmd.byte_addr,
        c3_p4_cmd_empty     => c3_p4_out.cmd.empty,
        c3_p4_cmd_full      => c3_p4_out.cmd.full,
        c3_p4_rd_clk        => c3_p4_in.rd.clk,
        c3_p4_rd_en         => c3_p4_in.rd.en,
        c3_p4_rd_data       => c3_p4_out.rd.data,
        c3_p4_rd_full       => c3_p4_out.rd.full,
        c3_p4_rd_empty      => c3_p4_out.rd.empty,
        c3_p4_rd_count      => c3_p4_out.rd.count,
        c3_p4_rd_overflow   => c3_p4_out.rd.overflow,
        c3_p4_rd_error      => c3_p4_out.rd.error,


        c3_p5_cmd_clk       => c3_p5_in.cmd.clk,
        c3_p5_cmd_en        => c3_p5_in.cmd.en,
        c3_p5_cmd_instr     => c3_p5_in.cmd.instr,
        c3_p5_cmd_bl        => c3_p5_in.cmd.bl,
        c3_p5_cmd_byte_addr => c3_p5_in.cmd.byte_addr,
        c3_p5_cmd_empty     => c3_p5_out.cmd.empty,
        c3_p5_cmd_full      => c3_p5_out.cmd.full,
        c3_p5_wr_clk        => c3_p5_in.wr.clk,
        c3_p5_wr_en         => c3_p5_in.wr.en,
        c3_p5_wr_mask       => c3_p5_in.wr.mask,
        c3_p5_wr_data       => c3_p5_in.wr.data,
        c3_p5_wr_full       => c3_p5_out.wr.full,
        c3_p5_wr_empty      => c3_p5_out.wr.empty,
        c3_p5_wr_count      => c3_p5_out.wr.count,
        c3_p5_wr_underrun   => c3_p5_out.wr.underrun,
        c3_p5_wr_error      => c3_p5_out.wr.error);
    
    U_C3_P1_SPLITTER : entity work.util_bidir_ram_port_splitter port map (
        clock => clk_ethernet,
        reset => reset,
        ram_in => c3_p1_in,
        ram_out => c3_p1_out,
        ram_rd_in => c3_p1_rdonly_in,
        ram_rd_out => c3_p1_rdonly_out,
        ram_wr_in => c3_p1_wronly_in,
        ram_wr_out => c3_p1_wronly_out);

    process (reset, BTNU, BTND, BTNC, c3_p0_out, c3_p0_in, c3_p1_out, c3_p1_in, c3_p2_out, c3_p2_in, c3_p3_out, c3_p3_in, c3_p4_out, c3_p4_in, c3_p5_out, c3_p5_in) is
        variable violation, errors, overflowunderrun, usage : std_logic_vector(7 downto 0);
        variable led_tmp : std_logic_vector(7 downto 0);
    begin
        errors(0) := c3_p0_out.wr.error;
        errors(1) := c3_p0_out.rd.error;
        errors(2) := c3_p1_out.wr.error;
        errors(3) := c3_p1_out.rd.error;
        errors(4) := c3_p2_out.rd.error;
        errors(5) := c3_p3_out.rd.error;
        errors(6) := c3_p4_out.rd.error;
        errors(7) := c3_p5_out.wr.error;
        
        overflowunderrun(0) := c3_p0_out.wr.underrun;
        overflowunderrun(1) := c3_p0_out.rd.overflow;
        overflowunderrun(2) := c3_p1_out.wr.underrun;
        overflowunderrun(3) := c3_p1_out.rd.overflow;
        overflowunderrun(4) := c3_p2_out.rd.overflow;
        overflowunderrun(5) := c3_p3_out.rd.overflow;
        overflowunderrun(6) := c3_p4_out.rd.overflow;
        overflowunderrun(7) := c3_p5_out.wr.underrun;
        
        if BTNU = '1' then
            led_tmp := violation;
        elsif BTND = '1' then
            led_tmp := overflowunderrun;
        elsif BTNC = '1' then
            led_tmp := errors;
        else
            led_tmp := usage;
        end if;
        led(6 downto 0) <= led_tmp(6 downto 0);
        if led_tmp(7) = '1' then -- make sure not to drive led(7) low because JP11 can short it to VCC
            led(7) <= '1';
        else
            led(7) <= 'Z';
        end if;
        
        if rising_edge(c3_p0_in.wr.clk) then usage(0) := c3_p0_in.wr.en; end if;
        if rising_edge(c3_p0_in.rd.clk) then usage(1) := c3_p0_in.rd.en; end if;
        if rising_edge(c3_p1_in.wr.clk) then usage(2) := c3_p1_in.wr.en; end if;
        if rising_edge(c3_p1_in.rd.clk) then usage(3) := c3_p1_in.rd.en; end if;
        if rising_edge(c3_p2_in.rd.clk) then usage(4) := c3_p2_in.rd.en; end if;
        if rising_edge(c3_p3_in.rd.clk) then usage(5) := c3_p3_in.rd.en; end if;
        if rising_edge(c3_p4_in.rd.clk) then usage(6) := c3_p4_in.rd.en; end if;
        if rising_edge(c3_p5_in.wr.clk) then usage(7) := c3_p5_in.wr.en; end if;
        
        if reset = '1' then violation(0) := '0'; elsif rising_edge(c3_p0_in.wr.clk) then if (c3_p0_in.wr.en and c3_p0_out.wr.full ) = '1' then violation(0) := '1'; end if; end if;
        if reset = '1' then violation(1) := '0'; elsif rising_edge(c3_p0_in.rd.clk) then if (c3_p0_in.rd.en and c3_p0_out.rd.empty) = '1' then violation(1) := '1'; end if; end if;
        if reset = '1' then violation(2) := '0'; elsif rising_edge(c3_p1_in.wr.clk) then if (c3_p1_in.wr.en and c3_p1_out.wr.full ) = '1' then violation(2) := '1'; end if; end if;
        if reset = '1' then violation(3) := '0'; elsif rising_edge(c3_p1_in.rd.clk) then if (c3_p1_in.rd.en and c3_p1_out.rd.empty) = '1' then violation(3) := '1'; end if; end if;
        if reset = '1' then violation(4) := '0'; elsif rising_edge(c3_p2_in.rd.clk) then if (c3_p2_in.rd.en and c3_p2_out.rd.empty) = '1' then violation(4) := '1'; end if; end if;
        if reset = '1' then violation(5) := '0'; elsif rising_edge(c3_p3_in.rd.clk) then if (c3_p3_in.rd.en and c3_p3_out.rd.empty) = '1' then violation(5) := '1'; end if; end if;
        if reset = '1' then violation(6) := '0'; elsif rising_edge(c3_p4_in.rd.clk) then if (c3_p4_in.rd.en and c3_p4_out.rd.empty) = '1' then violation(6) := '1'; end if; end if;
        if reset = '1' then violation(7) := '0'; elsif rising_edge(c3_p5_in.wr.clk) then if (c3_p5_in.wr.en and c3_p5_out.wr.full ) = '1' then violation(7) := '1'; end if; end if;
    end process;


    U_DUMMY_SYNC_GEN : entity work.video_sync_recovery port map (
        valid => '1',
        pixel_clock => clk_pixel,
        hsync => '0', -- without hsync or vsync, video_sync_recovery will run free
        vsync => '0',
        sync_out => dummy_video.sync);
    U_DUMMY_PATTERN_GEN : entity work.video_pattern_generator port map (
        sync => dummy_video.sync,
        data_out => dummy_video.data);

    U_DVI_RX : entity work.dvi_receiver
        port map(rst          => reset,
                 rx_tmds      => rx_tmds,
                 rx_tmdsb     => rx_tmdsb,
                 video_output => received_video);
    U_EDID : entity work.edid_wrapper
        port map(clock => clk_100MHz_buf,
                 reset => reset,
                 scl   => rx_scl,
                 sda   => rx_sda);

    U_SRC_MUX : entity work.video_mux
        port map(video0    => dummy_video,
                 video1    => received_video,
                 sel       => received_video.sync.valid,
                 video_out => overlay_video);

    U_DISTORTER : entity work.video_distorter
        generic map (
            LEFT_CAMERA_MEMORY_LOCATION => LEFT_CAMERA_MEMORY_LOCATION,
            RIGHT_CAMERA_MEMORY_LOCATION => RIGHT_CAMERA_MEMORY_LOCATION,
            PREFETCHER_TABLE_MEMORY_LOCATION => DISTORTER_PREFETCHER_TABLE_MEMORY_LOCATION,
            MAP_MEMORY_LOCATION => DISTORTER_MAP_MEMORY_LOCATION)
        port map (
            sync     => overlay_video.sync,
            data_out => base_video_data,
            ram1_in  => c3_p2_in,
            ram1_out => c3_p2_out,
            ram2_in  => c3_p3_in,
            ram2_out => c3_p3_out,
            ram3_in  => c3_p4_in,
            ram3_out => c3_p4_out);

    U_OVERLAY : entity work.video_overlay
        port map(video_sync  => overlay_video.sync,
                 video_over  => overlay_video.data,
                 video_under => base_video_data,
                 video_out   => composite_video);

    U_DVI_TX : entity work.dvi_transmitter
        port map(video_in => composite_video,
                 tx_tmds  => tx_tmds,
                 tx_tmdsb => tx_tmdsb);



    U_UART : entity work.uart_transmitter
        generic map(
            CLOCK_FREQUENCY => 100000000.0,
            BAUD_RATE => 4000000.0)
        port map (
            clock => clk_100MHz_buf,
            reset => reset,
            tx    => uart_tx,
            ready => uart_tx_ready,
            data  => uart_tx_data,
            write => uart_tx_write);

    U_UART2 : entity work.uart_receiver
        generic map(
            CLOCK_FREQUENCY => 100000000.0,
            BAUD_RATE => 4000000.0)
        port map (
            clock => clk_100MHz_buf,
            reset => reset,
            rx    => uart_rx,
            valid => uart_rx_valid,
            data  => uart_rx_data);

    U_UART_RAM : entity work.uart_ram_interface
        port map (
            clock => clk_100MHz_buf,
            reset => reset,
            ram_in => c3_p0_in,
            ram_out => c3_p0_out,
            uart_tx_ready => uart_tx_ready,
            uart_tx_data => uart_tx_data,
            uart_tx_write => uart_tx_write,
            uart_rx_valid => uart_rx_valid,
            uart_rx_data => uart_rx_data,
            arbiter_in => spi_arbiter_users_in(0),
            arbiter_out => spi_arbiter_users_out(0),
            pair7P => pair7P,
            pair7N => pair7N,
            pair8P => pair8P,
            pair8N => pair8N,
            pair9P => pair9P,
            pair9N => pair9N,
            pair12N => pair12N,
            pair13N => pair13N,
            pair14P => pair14P,
            pair14N => pair14N,
            SCLK => SCLK);
    
    reset_for_ram_user <= reset or not c3_calib_done or c3_rst0;
    
    U_CAMERA_ETHERNET_WRITER : entity work.camera_ethernet_writer
        generic map (
            BUFFER_ADDRESS => RIGHT_CAMERA_MEMORY_LOCATION)
        port map (
            ram_in => c3_p1_rdonly_in,
            ram_out => c3_p1_rdonly_out,
            clock_ethernet => clk_ethernet,
            reset => reset_for_ram_user,
            phy_in => phy_in,
            phy_out => phy_out);
    
    phyrst <= not phy_in.rst;
    U_PHY_GTXCLK_ODDR : oddr2
        generic map(
            ddr_alignment => "c1",      -- sets output alignment to "none", "c0", "c1"
            init          => '0',       -- sets initial state of the q output to '0' or '1'
            srtype        => "async"    -- specifies "sync" or "async" set/reset
        ) port map(
            q => phygtxclk,
            c0 => phy_in.gtxclk,
            c1 => not phy_in.gtxclk,
            ce => '1',
            d0 => '0',
            d1 => '1',
            r => '0',
            s => '0');
    phytxd  <= phy_in.txd;
    phytxen <= phy_in.txen;
    phytxer <= phy_in.txer;

    phymdc <= '0';
    phymdi <= 'Z';
end architecture RTL;
