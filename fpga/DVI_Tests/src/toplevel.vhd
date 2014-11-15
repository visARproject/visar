library ieee;
use ieee.std_logic_1164.all;
use work.video_bus.all;
use work.ram_port.all;

library unisim;
use unisim.vcomponents.all;

entity toplevel is
    port (
        clk_100MHz : in std_logic;
        rst_n : in std_logic;
        rx_tmds : in std_logic_vector(3 downto 0);
        rx_tmdsb : in std_logic_vector(3 downto 0);
        tx_tmds : out std_logic_vector(3 downto 0);
        tx_tmdsb : out std_logic_vector(3 downto 0);
        rx_sda : inout std_logic;
        rx_scl : inout std_logic;
        led : out std_logic_vector(0 downto 0);
        
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
    signal clk_100MHz_buf : std_logic;
    
    signal clk_132MHz : std_logic;
    signal pattern_gen_video_out : video_bus;
    signal mux_video_out, dvi_rx_video_out : video_bus;
    signal rst : std_logic;
    signal combiner_video_out : video_bus;
    signal combiner_video_under_in : video_data;
    
    signal c3_sys_clk : std_logic;
    signal c3_sys_rst_i : std_logic;
    signal c3_calib_done : std_logic;
    signal c3_clk0       : std_logic;
    signal c3_rst0       : std_logic;
    
    signal c3_p0_in : ram_bidir_port_in;
    signal c3_p0_out : ram_bidir_port_out;
    
    signal c3_p1_in : ram_bidir_port_in;
    signal c3_p1_out : ram_bidir_port_out;
    
    signal c3_p2_in : ram_wr_port_in;
    signal c3_p2_out : ram_wr_port_out;
    
    signal c3_p3_in : ram_rd_port_in;
    signal c3_p3_out : ram_rd_port_out;
begin
    IBUFG_inst : IBUFG
        port map(
            O => clk_100MHz_buf, -- Clock buffer output
            I => clk_100MHz      -- Clock buffer input (connect directly to top-level port)
        );
    
    c3_sys_clk <= clk_100MHz_buf;
    c3_sys_rst_i <= not rst;
    
    u_dram : entity work.dram port map (
        c3_sys_clk          => c3_sys_clk,
        c3_sys_rst_i        => c3_sys_rst_i,                        
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
        c3_p2_wr_clk        => c3_p2_in.wr.clk,
        c3_p2_wr_en         => c3_p2_in.wr.en,
        c3_p2_wr_mask       => c3_p2_in.wr.mask,
        c3_p2_wr_data       => c3_p2_in.wr.data,
        c3_p2_wr_full       => c3_p2_out.wr.full,
        c3_p2_wr_empty      => c3_p2_out.wr.empty,
        c3_p2_wr_count      => c3_p2_out.wr.count,
        c3_p2_wr_underrun   => c3_p2_out.wr.underrun,
        c3_p2_wr_error      => c3_p2_out.wr.error,
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
        c3_p3_rd_error      => c3_p3_out.rd.error);

    rst <= not rst_n;
    
    U_DVI_RX : entity work.dvi_receiver
        port map(rst          => rst,
                 rx_tmds      => rx_tmds,
                 rx_tmdsb     => rx_tmdsb,
                 video_output => dvi_rx_video_out);
    
    led(0) <= dvi_rx_video_out.sync.valid;
    
    U_PIXEL_CLK_GEN : entity work.pixel_clk_gen
        port map(CLK_IN1  => clk_100MHz_buf,
                 CLK_OUT1 => clk_132MHz,
                 RESET    => '0',
                 LOCKED   => open);
    
    U_PATTERN_GEN : entity work.video_pattern_generator
        port map(
                reset => rst,
                clk_in => clk_132MHz,
                video  => pattern_gen_video_out);
                
    combiner_video_under_in.blue <= x"FF";
    combiner_video_under_in.red <= x"00";
    combiner_video_under_in.green <= x"00";                

    U_OVERLAY : entity work.video_overlay
        port map(video_over  => pattern_gen_video_out.data,
                 video_under => combiner_video_under_in,
                 video_out   => combiner_video_out.data);
                 
    combiner_video_out.sync <= pattern_gen_video_out.sync;
 
    U_SRC_MUX : entity work.video_mux
        port map(video0    => combiner_video_out,
                 video1    => dvi_rx_video_out,
                 sel       => dvi_rx_video_out.sync.valid,
                 video_out => mux_video_out);        
                 
    U_DVI_TX : entity work.dvi_transmitter
        port map(video_in => mux_video_out,
                 tx_tmds  => tx_tmds,
                 tx_tmdsb => tx_tmdsb);  
 
    U_EDID : entity work.edid_wrapper
        port map(clk_132MHz => clk_132MHz,
                 reset        => rst,
                 scl        => rx_scl,
                 sda        => rx_sda);
                 
end architecture RTL;
