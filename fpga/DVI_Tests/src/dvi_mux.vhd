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
	signal sel_last, sel_last_last : std_logic;
	signal valid_shift_reg : std_logic_vector(9 downto 0);
begin
	
	process(px_clk_out)
	begin
		if rising_edge(px_clk_out) then
			sel_last <= sel;
			sel_last_last <= sel_last;
			if sel_last_last /= sel_last then
				valid_shift_reg <= (others => '0');
			end if;
			
			valid_shift_reg <= valid_shift_reg(valid_shift_reg'length-2 downto 0) & '1';
		end if;
	end process;
	
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
			video_out.valid <= video0.valid and valid_shift_reg(valid_shift_reg'length-1);
		elsif sel = '1' then
			video_out.blue <= video1.blue;
			video_out.red <= video1.red;	
			video_out.green <= video1.green;
			video_out.frame_rst <= video1.frame_rst;	
			video_out.valid <= video1.valid and valid_shift_reg(valid_shift_reg'length-1);
		end if;
		
	end process;
	
	
			     
	
end architecture RTL;
