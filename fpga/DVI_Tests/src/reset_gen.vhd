library ieee;
use ieee.std_logic_1164.all;

entity reset_gen is
	generic (
		LENGTH : natural := 10);
	port (
		clock     : in  std_logic;
		reset_in  : in  std_logic;  -- asynchronous
		reset_out : out std_logic); -- synchronous, always at least LENGTH clock cycles long
end entity reset_gen;


architecture RTL of reset_gen is
	signal shift : std_logic_vector(LENGTH-1 downto 0) := (others => '1');
begin
	process(reset_in, clock)
	begin
		if reset_in = '1' then
			shift <= (others => '1');
		elsif rising_edge(clock) then
			shift <= shift(shift'length-2 downto 0) & '0';
		end if;
	end process;
	
	reset_out <= shift(shift'length-1);
end architecture RTL;
