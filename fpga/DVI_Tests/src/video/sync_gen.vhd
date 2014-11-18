----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    00:06:13 10/25/2014 
-- Design Name: 
-- Module Name:    video_sync_gen - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--
----------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.video_bus.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity video_sync_gen is
	port (
		video 		: in video_bus;
		h_sync 		: out std_logic;
		v_sync 		: out std_logic;
		data_en 	: out std_logic
	);
end entity video_sync_gen;


architecture Behavioral of video_sync_gen is
	signal h_cnt : std_logic_vector(11 downto 0) := (others => '0');
	signal v_cnt : std_logic_vector(11 downto 0) := (others => '0');
	
begin
	process (video.sync.pixel_clk) is
	begin
		if rising_edge(video.sync.pixel_clk) then
			if unsigned(h_cnt) /= H_MAX - 1 then
				h_cnt <= std_logic_vector(unsigned(h_cnt) + 1);
			elsif unsigned(h_cnt) = H_MAX - 1 and unsigned(v_cnt) /= V_MAX - 1 then
				h_cnt <= (others => '0');
				v_cnt <= std_logic_vector(unsigned(v_cnt) + 1);
			end if;
			
			if((unsigned(h_cnt) < H_DISPLAY_END) and (unsigned(v_cnt) < V_DISPLAY_END)) then
				data_en <= '1';
			else
				data_en <= '0';		
			end if;
			
			-- +hsync -vsync
			
			if((unsigned(h_cnt) >= HSYNC_BEGIN) and (unsigned(h_cnt) < HSYNC_END)) then
				h_sync <= '1';
			else
				h_sync <= '0';
			end if;
			
			if((unsigned(v_cnt) >= VSYNC_BEGIN) and (unsigned(v_cnt) < VSYNC_END)) then
				v_sync <= '0';
			else
				v_sync <= '1';
			end if;
			
			-- If the frame reset comes in, then reset the counters.
			if video.sync.frame_rst = '1' then
				h_cnt <= (others => '0');
				v_cnt <= (others => '0');
			end if;
		end if;
	end process;

end Behavioral;

