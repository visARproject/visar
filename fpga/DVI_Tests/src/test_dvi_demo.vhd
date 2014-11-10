library ieee;
use ieee.std_logic_1164.all;
use work.video_bus.all;


entity test_dvi_demo is
    port (
        clk_100MHz : in std_logic;
        rst_n : in std_logic;
        rx_tmds : in std_logic_vector(3 downto 0);
        rx_tmdsb : in std_logic_vector(3 downto 0);
        tx_tmds : out std_logic_vector(3 downto 0);
        tx_tmdsb : out std_logic_vector(3 downto 0);
        led : out std_logic_vector(0 downto 0)
    );
end entity test_dvi_demo;


architecture RTL of test_dvi_demo is
    signal clk_132MHz : std_logic;
    signal pattern_gen_video_out : video_bus;
    signal mux_video_out, dvi_rx_video_out : video_bus;
    signal rst : std_logic;
begin
	rst <= not rst_n;
	
	U_DVI_RX : entity work.dvi_receiver
		port map(rst          => rst,
			     rx_tmds      => rx_tmds,
			     rx_tmdsb     => rx_tmdsb,
			     video_output => dvi_rx_video_out);
    
    led(0) <= dvi_rx_video_out.valid;
	
    U_PIXEL_CLK_GEN : entity work.pixel_clk_gen
        port map(CLK_IN1  => clk_100MHz,
                 CLK_OUT1 => clk_132MHz,
                 RESET    => '0',
                 LOCKED   => open);
    
    U_PATTERN_GEN : entity work.dvi_video_test_pattern_generator
        port map(
                reset => rst,
                clk_in => clk_132MHz,
                 video  => pattern_gen_video_out);
                 
    U_SRC_MUX : entity work.dvi_mux
        port map(video0    => pattern_gen_video_out,
                 video1    => dvi_rx_video_out,
                 sel       => dvi_rx_video_out.valid,
                 video_out => mux_video_out);        
                 
    U_DVI_TX : entity work.dvi_transmitter
        port map(video_in => mux_video_out,
                 tx_tmds  => tx_tmds,
                 tx_tmdsb => tx_tmdsb);  
 
    
end architecture RTL;
