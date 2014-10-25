library IEEE;
use IEEE.std_logic_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb is
end tb;

architecture Behavioral of tb is
    signal reset_l : std_logic := '0';
    signal clk : std_logic := '0';
    signal pclk : std_logic := '0';
begin
    uut : entity work.VmodCAM_Ref
        port map(
			CLK_I => clk,
            RESET_I => reset_l,
            SW_I => "00000000",
            phytxclk => '0',
            phyRXD => "00000000",
            phyrxdv => '0',
            phyrxer => '0',
            phyrxclk => '0',
            phyint => '0',
            phycrs => '0',
            phycol => '0',
            
            CAMA_PCLK_I => pclk,
            CAMA_LV_I => '1');
    
    clk <= not clk after 5 ns;
    
    pclk <= not pclk after 6.25 ns;

    reset_proc : process
    begin
        wait for 1 us;
        reset_l <= '1';
        wait;
    end process;
end Behavioral;
