library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity util_spi_master_tb is
end entity;

architecture arc of util_spi_master_tb is
    constant DATA_BITS : positive := 16;
    
    signal clock : std_logic := '0';
    signal reset : std_logic := '1';
    
    signal data_in  : std_logic_vector(DATA_BITS-1 downto 0);
    signal start    : std_logic;
    signal busy     : std_logic;
    signal data_out : std_logic_vector(DATA_BITS-1 downto 0);
    
    signal nSS  : std_logic;
    signal SCLK : std_logic;
    signal MOSI : std_logic;
    signal MISO : std_logic;
begin
    UUT : entity work.util_spi_master
        generic map (
            CLOCK_FREQUENCY => 100.0E6,
            SCLK_FREQUENCY => 1.0E6,
            DATA_BITS => DATA_BITS)
        port map (
            clock => clock,
            reset => reset,
            
            data_in  => data_in,
            start    => start,
            busy     => busy,
            data_out => data_out,
            
            nSS  => nSS,
            SCLK => SCLK,
            MOSI => MOSI,
            MISO => MISO);
    
    clock <= not clock after 10 ns;
    
    process is
    begin
        wait for 1 us;
        
        wait until rising_edge(clock);
        reset <= '0';
        
        wait for 1 us;
        
        wait until rising_edge(clock);
        data_in <= "0100001000110111";
        start <= '1';
        wait until rising_edge(clock);
        start <= '0';
        
        wait;
    end process;
end architecture;
