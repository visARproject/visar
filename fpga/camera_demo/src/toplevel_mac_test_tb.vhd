library IEEE;
use IEEE.std_logic_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity toplevel_mac_test_tb is
end toplevel_mac_test_tb;

architecture Behavioral of toplevel_mac_test_tb is
    signal reset_l : std_logic := '0';
    signal clk : std_logic := '0';
begin
    uut : entity work.toplevel_mac_test
        port map(
			CLK_I => clk,
            RESET_I => reset_l,
            phytxclk => '0',
            phyRXD => "00000000",
            phyrxdv => '0',
            phyrxer => '0',
            phyrxclk => '0',
            phyint => '0',
            phycrs => '0',
            phycol => '0');
    
    clk <= not clk after 5 ns;

    reset_proc : process
    begin
        wait for 1 us;
        reset_l <= '1';
        wait;
    end process;
end Behavioral;
