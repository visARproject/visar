library ieee;
use ieee.std_logic_1164.all;


entity dvi_test_tb is
end entity dvi_test_tb;



architecture RTL of dvi_test_tb is

	signal clk_100MHz : std_logic := '0';
	signal rst_n : std_logic;
	signal tmds : std_logic_vector(3 downto 0);
	signal tmdsb : std_logic_vector(3 downto 0);
	
begin
	UUT : entity work.test_dvi_demo
		port map(clk_100MHz => clk_100MHz,
			     rst_n        => rst_n,
			     tmds       => tmds,
			     tmdsb      => tmdsb);
			     
	clk_100MHz <= not clk_100MHz after 5 ns;
	     
	process
	begin
		rst_n <= '1';
		
		wait for 20 ns;
		
		rst_n <= '0';
		
		wait;
	
	
	end process;		     
			   
			   
end architecture RTL;
