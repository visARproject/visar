----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    22:54:50 10/23/2014 
-- Design Name: 
-- Module Name:    test_dvi_decoder - Behavioral 
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
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use WORK.VIDEO_BUS.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity test_dvi_decoder is
	port(
		clk_in 	: in std_logic;
		video : out video_bus;)
end test_dvi_decoder;

architecture Behavioral of test_dvi_decoder is
	constant h_max : natural := 1138;
	constant v_max : natural := 1933;
	signal h_cnt : std_logic_vector(11 downto 0) := (others => '0');
	signal v_cnt : std_logic_vector(11 downto 0) := (others => '0');	
begin

	process(clk_in)
	begin
		if(rising_edge(clk_in)) then
			video.frame_rst <= '0';
			if unsigned(h_cnt) /= h_max and unsigned(v_cnt) /= v_max  then
				h_cnt <= h_cnt + 1;
			elsif unsigned(h_cnt) = h_max and unsigned(v_cnt) /= v_max then
				h_cnt <= (others => '0');
				v_cnt <= v_cnt + 1;
			elsif unsigned(h_cnt) = h_max and unsigned(v_cnt) = v_max then
				video.frame_rst <= '1';
				h_cnt <= (others => '0');
				v_cnt <= (others => '0');
			end if;
			
			if ((unsigned(h_cnt) / 16) mod 2 ) = '0' xor ((unsigned(v_cnt) / 16) mod 2 ) = '0' then
				video.red <= x'FF';
				video.green <= x'FF';
				video.blue <= x'FF';
			else
				video.red <= x'00';
				video.green <= x'00';
				video.blue <= x'00';
			end if;
		end if;
		
		video.pixel_clk <= clk_in;
	
	
	end process;


end Behavioral;

