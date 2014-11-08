----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    23:09:16 10/23/2014 
-- Design Name: 
-- Module Name:    counter - Behavioral 
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
-- Counter is max inclusive
----------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity counter is
  generic(
  	width 	: positive := 10;
  	max	  	: positive := 1024);
  port (
    clk    : in  std_logic;
    rst    : in  std_logic;
    up   : in  std_logic;            
    load : in  std_logic;            
    input  : in  std_logic_vector(width downto 0);
    output : out std_logic_vector(width downto 0));
end counter;

architecture seq of counter is
	signal current_val : std_logic_vector(width downto 0);
begin
	process(rst, clk)
		variable temp : unsigned(width downto 0);
	begin
		if(rising_edge(clk)) then
			if(rst = '1') then
				current_val <= (others => '0');
			elsif(load = '1') then
				current_val <= input;
			else
				if(up = '1') then
					if (unsigned(current_val) = max) then
						current_val <= (others => '0');
					else
						temp := unsigned(current_val) + 1;
						current_val <= std_logic_vector(temp);
					end if;
				else
					temp := unsigned(current_val) - 1;
					current_val <= std_logic_vector(temp);
				end if;
			end if;			
		end if;
	end process;
	
	output <= current_val;
end seq;

