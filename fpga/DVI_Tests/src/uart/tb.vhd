library ieee;
use ieee.std_logic_1164.all;

entity uart_tb is
end entity uart_tb;

architecture RTL of uart_tb is
    constant DATA_BITS : natural := 8;
    
    signal clock : std_logic := '0';
    signal reset : std_logic := '1';
    signal tx : std_logic;
    signal ready : std_logic;
    signal data : std_logic_vector(DATA_BITS-1 downto 0);
    signal write : std_logic;
begin
    UUT : entity work.uart_transmitter
        generic map (
            DATA_BITS => DATA_BITS,
            CLOCK_FREQUENCY => 100.0e6,
            BAUD_RATE => 9600.0)
        port map (
            clock => clock,
            reset => reset,
            tx    => tx,
            ready => ready,
            data  => data,
            write => write);
    
    UUT2 : entity work.uart_receiver
        generic map (
            DATA_BITS => DATA_BITS,
            CLOCK_FREQUENCY => 100.0e6,
            BAUD_RATE => 9600.0)
        port map (
            clock => clock,
            reset => reset,
            rx    => tx);
    
    clock <= not clock after 5 ns;
    
    process
    begin
        wait for 1 us;
        
        reset <= '0';
        
        wait;
    end process;
    
    process(clock)
    begin
        if rising_edge(clock) then
            data <= x"A7";
            write <= ready;
        end if;
    end process;
end architecture RTL;
