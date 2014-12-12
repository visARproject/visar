library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;


entity ram_streamer_tb is
end entity ram_streamer_tb;

architecture RTL of ram_streamer_tb is
    constant WORDS : integer := 5;
    
    signal clock  : std_logic := '0';
    signal reset  : std_logic;
    signal en     : std_logic;
    signal output : std_logic_vector(32*WORDS-1 downto 0);
    
    signal ram_in  : ram_rd_port_in;
    signal ram_out : ram_rd_port_out;
begin
    clock <= not clock after 5 ns;
    
    U_ram_port : entity work.mock_ram_port port map (
        ram_in => ram_in,
        ram_out => ram_out);
    
    UUT : entity work.ram_streamer
        generic map (
            MEMORY_LOCATION => 1236,
            WORDS => WORDS)
        port map (
            ram_in => ram_in,
            ram_out => ram_out,
            clock => clock,
            reset => reset,
            en => en,
            output => output);
    
    process
    begin
        reset <= '1';
        en <= '0';
        
        wait for 1 us;
        wait until rising_edge(clock);
        reset <= '0';
        
        wait for 10 us;
        wait until rising_edge(clock);
        en <= '1';
        
        wait until rising_edge(clock);
        en <= '0';
        
        wait for 10 us;
        wait until rising_edge(clock);
        en <= '1';
        
        wait until rising_edge(clock);
        en <= '0';
        
        wait;
    end process;
end architecture RTL;
