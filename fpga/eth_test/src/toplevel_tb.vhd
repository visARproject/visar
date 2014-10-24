library IEEE;
use IEEE.std_logic_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb is
end tb;

architecture Behavioral of tb is
    signal reset_l : std_logic := '0';
    signal clk : std_logic := '0';
	 signal btn_1 : std_logic := '0';
begin
    uut : entity work.toplevel
        port map(
			clk => clk,
            btn => "0000" & btn_1 & reset_l,
            phytxclk => '0',
            phyRXD => "00000000",
            phyrxdv => '0',
            phyrxer => '0',
            phyrxclk => '0',
            phyint => '0',
            phycrs => '0',
            phycol => '0');
    
    clk <= not clk after 10 ns;

    reset_proc : process
    begin
        wait for 1 us;
        reset_l <= '1';
        wait;
    end process;

	 button_proc : process
	 begin
	     wait for 2 us;
		  btn_1 <= '1';
		  wait;
	 end process;
end Behavioral;
