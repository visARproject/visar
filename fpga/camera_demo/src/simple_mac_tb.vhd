library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.simple_mac_pkg.all;


entity simple_mac_tb is
end simple_mac_tb;

architecture Behavioral of simple_mac_tb is
    signal reset : std_logic := '1';
    signal clk : std_logic := '0';
    signal phy_in : PHYInInterface;
    signal phy_out : PHYOutInterface;
    signal mac_in : MACInInterface := (tx_flag => '0', tx_data => "UUUUUUUU", tx_eop => '0');
    signal mac_out : MACOutInterface;
    signal pos : integer := 0;
    type BufType is array (0 to 60) of std_logic_vector(7 downto 0);
    signal buf : BufType := ("UUUUUUUU", x"00", x"10", x"A4", x"7B", x"EA", x"80", x"00", x"12", x"34", x"56", x"78", x"90", x"08", x"00", x"45", x"00", x"00", x"2E", x"B3", x"FE", x"00", x"00", x"80", x"11", x"05", x"40", x"C0", x"A8", x"00", x"2C", x"C0", x"A8", x"00", x"04", x"04", x"00", x"04", x"00", x"00", x"1A", x"2D", x"E8", x"00", x"01", x"02", x"03", x"04", x"05", x"06", x"07", x"08", x"09", x"0A", x"0B", x"0C", x"0D", x"0E", x"0F", x"10", x"11");
begin
    uut : entity work.simple_mac
        port map(
            clk_125M => clk,
            reset => reset,
            
            phy_in => phy_in,
            phy_out => phy_out,
            
            mac_in => mac_in,
            mac_out => mac_out);
    
    clk <= not clk after 4 ns;

    reset_proc : process
    begin
        wait for 1 us;
        reset <= '0';
        wait;
    end process;
    
    start_proc : process
    begin
        wait for 10 us;
        mac_in.tx_flag <= '1';
        wait;
    end process;
    
    data_proc : process(clk)
    begin
        if rising_edge(clk) and mac_out.tx_rd = '1' then
            pos <= pos + 1;
        end if;
    end process;
    
    mac_in.tx_data <= buf(pos);
    mac_in.tx_eop <= '1' when pos = 60 else '0';
end Behavioral;
