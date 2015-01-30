library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.video_bus.all;
use work.ram_port.all;
use work.camera.all;

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
        led : out std_logic_vector(0 downto 0);

        -- Camera A and B interface
        camera_a_out    : out   camera_out;
        camera_a_inout  : inout camera_inout;
        camera_b_out    : out   camera_out;
        camera_b_inout  : inout camera_inout;
        camera_x_vdd_en : out   std_logic;

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
        mcb3_dram_ck_n   : out std_logic);
end entity toplevel;


architecture RTL of toplevel is
    signal reset          : std_logic;
    signal clk_100MHz_buf : std_logic;
    signal clk_132MHz     : std_logic;
    signal clk_24MHz      : std_logic;

    signal camera_a_vdd_en, camera_b_vdd_en : std_logic;
    signal camera_a_output, camera_b_output : camera_output;

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

    signal c3_p2_in  : ram_rd_port_in;
    signal c3_p2_out : ram_rd_port_out;

    signal c3_p3_in  : ram_rd_port_in;
    signal c3_p3_out : ram_rd_port_out;

    signal c3_p4_in  : ram_wr_port_in;
    signal c3_p4_out : ram_wr_port_out;

    signal c3_p5_in  : ram_wr_port_in;
    signal c3_p5_out : ram_wr_port_out;


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
begin
    reset <= not rst_n;

    IBUFG_inst : IBUFG
        port map(
            O => clk_100MHz_buf, -- Clock buffer output
            I => clk_100MHz      -- Clock buffer input (connect directly to top-level port)
        );

    U_PIXEL_CLK_GEN : entity work.pixel_clk_gen port map (
        CLK_IN_100MHz     => clk_100MHz_buf,
        CLK_OUT_132MHz    => clk_132MHz,
        CLK_OUT_24MHz     => clk_24MHz,
        RESET             => '0',
        LOCKED            => open);
    

    U_CAMERA_A_WRAPPER : entity work.camera_wrapper port map (
        clock_24MHz     => clk_24MHz,
        reset           => reset,
        
        camera_out => camera_a_out,
        camera_inout => camera_a_inout,
        camera_vdd_en => camera_a_vdd_en,
        
        output => camera_a_output);
    
    U_CAMERA_B_WRAPPER : entity work.camera_wrapper port map (
        clock_24MHz     => clk_24MHz,
        reset           => reset,
        
        camera_out => camera_b_out,
        camera_inout => camera_b_inout,
        camera_vdd_en => camera_b_vdd_en,
        
        output => camera_b_output);

    camera_x_vdd_en <= camera_a_vdd_en and camera_b_vdd_en;
    
    U_CAMERA_A_WRITER : entity work.camera_writer
        generic map (
            BUFFER_ADDRESS => LEFT_CAMERA_MEMORY_LOCATION)
        port map (
            camera_output => camera_a_output,
            
            ram_in  => c3_p4_in,
            ram_out => c3_p4_out);
    
    U_CAMERA_B_WRITER : entity work.camera_writer
        generic map (
            BUFFER_ADDRESS => RIGHT_CAMERA_MEMORY_LOCATION)
        port map (
            camera_output => camera_b_output,
            
            ram_in  => c3_p5_in,
            ram_out => c3_p5_out);

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
        c3_p4_wr_clk        => c3_p4_in.wr.clk,
        c3_p4_wr_en         => c3_p4_in.wr.en,
        c3_p4_wr_mask       => c3_p4_in.wr.mask,
        c3_p4_wr_data       => c3_p4_in.wr.data,
        c3_p4_wr_full       => c3_p4_out.wr.full,
        c3_p4_wr_empty      => c3_p4_out.wr.empty,
        c3_p4_wr_count      => c3_p4_out.wr.count,
        c3_p4_wr_underrun   => c3_p4_out.wr.underrun,
        c3_p4_wr_error      => c3_p4_out.wr.error,


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
    c3_p1_in <= (
        cmd => c3_p1_rdonly_in.cmd,
        rd => c3_p1_rdonly_in.rd,
        wr => (
            clk => '0',
            en => '0',
            mask => (others => '-'),
            data => (others => '-')));
    c3_p1_rdonly_out <= (cmd => c3_p1_out.cmd, rd => c3_p1_out.rd);

    led(0) <= c3_calib_done;


    U_DUMMY_SYNC_GEN : entity work.video_sync_recovery port map (
        valid => '1',
        pixel_clock => clk_132MHz,
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
        port map(clk_132MHz => clk_132MHz,
                 reset      => reset,
                 scl        => rx_scl,
                 sda        => rx_sda);

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
            ram3_in  => c3_p1_rdonly_in,
            ram3_out => c3_p1_rdonly_out);

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
            CLOCK_FREQUENCY => 132000000.0,
            BAUD_RATE => 4000000.0)
        port map (
            clock => clk_132MHz,
            reset => reset,
            tx    => uart_tx,
            ready => uart_tx_ready,
            data  => uart_tx_data,
            write => uart_tx_write);

    U_UART2 : entity work.uart_receiver
        generic map(
            CLOCK_FREQUENCY => 132000000.0,
            BAUD_RATE => 4000000.0)
        port map (
            clock => clk_132MHz,
            reset => reset,
            rx    => uart_rx,
            valid => uart_rx_valid,
            data  => uart_rx_data);

    U_UART_RAM : entity work.uart_ram_interface
        port map (
            clock => clk_132MHz,
            reset => reset,
            ram_in => c3_p0_in,
            ram_out => c3_p0_out,
            uart_tx_ready => uart_tx_ready,
            uart_tx_data => uart_tx_data,
            uart_tx_write => uart_tx_write,
            uart_rx_valid => uart_rx_valid,
            uart_rx_data => uart_rx_data);
end architecture RTL;
