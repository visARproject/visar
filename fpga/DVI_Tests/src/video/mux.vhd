library ieee;
library UNISIM;
use ieee.std_logic_1164.all;
use work.video_bus.all;
use unisim.vcomponents.all;

entity video_mux is
	port (
		video0    : in video_bus;
		video1    : in video_bus;
		sel       : in std_logic;
		video_out : out video_bus
	);
end entity video_mux;


architecture RTL of video_mux is
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
			     I0 => video0.sync.pixel_clk,
			     I1 => video1.sync.pixel_clk,
			     S  => sel);
			     
			     
	video_out.sync.pixel_clk <= px_clk_out;
	
	process (px_clk_out) is
	begin
		if rising_edge(px_clk_out) then
			if sel = '0' then
				video_out.sync.frame_rst <= video0.sync.frame_rst;
				video_out.sync.valid <= video0.sync.valid and valid_shift_reg(valid_shift_reg'length-1);
				video_out.data <= video0.data;
			else
				video_out.sync.frame_rst <= video1.sync.frame_rst;
				video_out.sync.valid <= video1.sync.valid and valid_shift_reg(valid_shift_reg'length-1);
				video_out.data <= video1.data;
			end if;
		end if;
	end process;

end architecture RTL;
