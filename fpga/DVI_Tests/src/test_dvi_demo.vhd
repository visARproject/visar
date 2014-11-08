library ieee;
use ieee.std_logic_1164.all;
use work.video_bus.all;


entity test_dvi_demo is
	port (
		clk_100MHz : in std_logic;
		rst_n : in std_logic;
		tmds : out std_logic_vector(3 downto 0);
		tmdsb : out std_logic_vector(3 downto 0)
	);
end entity test_dvi_demo;


architecture RTL of test_dvi_demo is
	signal clk_132MHz : std_logic;
	signal video : video_bus;
	signal video_out : video_bus;
	signal rst : std_logic;
	
begin
	rst <= not rst_n;
	U_PIXEL_CLK_GEN : entity work.pixel_clk_gen
		port map(CLK_IN1  => clk_100MHz,
			     CLK_OUT1 => clk_132MHz,
			     RESET    => rst,
			     LOCKED   => open);
	
	U_PATTERN_GEN : entity work.dvi_video_test_pattern_generator
		port map(clk_in => clk_132MHz,
			     video  => video);
			     
	U_SRC_MUX : entity work.dvi_mux
		port map(video0    => video,
			     video1    => video,
			     sel       => '1',
			     video_out => video_out);		
			     
	U_DVI_TX : entity work.dvi_transmitter
		port map(rst      => rst,
			     video_in => video_out,
			     tx_tmds  => tmds,
			     tx_tmdsb => tmdsb);     
	
end architecture RTL;
