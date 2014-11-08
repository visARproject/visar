library ieee;
library UNISIM;
use ieee.std_logic_1164.all;
use work.video_bus.all;
use unisim.vcomponents.all;

entity dvi_mux is
	port (
		video0 : in video_bus;
		video1 : in video_bus;
		sel    : in std_logic;
		video_out : out video_bus
	);
end entity dvi_mux;


architecture RTL of dvi_mux is
	signal px_clk_out : std_logic;
begin
	
	U_BUFG_PX_CLK : component BUFGMUX
		port map(O  => px_clk_out,
			     I0 => video0.pixel_clk,
			     I1 => video1.pixel_clk,
			     S  => sel);
			     
			     
	video_out.pixel_clk <= px_clk_out;
	
	process(sel, video0, video1) 
	begin
		if sel = '0' then	
			video_out.blue <= video0.blue;
			video_out.red <= video0.red;	
			video_out.green <= video0.green;
			video_out.frame_rst <= video0.frame_rst;
		elsif sel = '1' then
			video_out.blue <= video1.blue;
			video_out.red <= video1.red;	
			video_out.green <= video1.green;
			video_out.frame_rst <= video1.frame_rst;	
		end if;
		
	end process;
	
	
			     
	
end architecture RTL;
