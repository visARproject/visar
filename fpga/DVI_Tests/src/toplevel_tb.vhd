library ieee;
use ieee.std_logic_1164.all;


entity toplevel_tb is
end entity toplevel_tb;



architecture RTL of toplevel_tb is

    signal clk_100MHz : std_logic := '0';
    signal rst_n : std_logic;
    signal tx_tmds, rx_tmds : std_logic_vector(3 downto 0);
    signal tx_tmdsb, rx_tmdsb : std_logic_vector(3 downto 0);
    signal uart_rx : std_logic;
    
    signal reset : std_logic;
    signal ready : std_logic;
    signal data : std_logic_vector(7 downto 0);
    signal write : std_logic;
begin
    UUT : entity work.toplevel
        port map(clk_100MHz => clk_100MHz,
                 rst_n      => rst_n,
                 rx_tmds    => rx_tmds,
                 rx_tmdsb   => rx_tmdsb,
                 tx_tmds    => tx_tmds,
                 tx_tmdsb   => tx_tmdsb,
                 uart_rx    => uart_rx);
    
    UART : entity work.uart_transmitter
        generic map (
            CLOCK_FREQUENCY => 100.0e6,
            BAUD_RATE => 4000000.0)
        port map (
            clock => clk_100MHz,
            reset => reset,
            tx    => uart_rx,
            ready => ready,
            data  => data,
            write => write);
    
    process(clk_100MHz)
    begin
        if rising_edge(clk_100MHz) then
            data <= x"A7";
            write <= ready;
        end if;
    end process;
    
    clk_100MHz <= not clk_100MHz after 5 ns;
         
    process
    begin
        rst_n <= '0';
        
        wait for 1 us;
        
        rst_n <= '1';
        
        wait;
    
    
    end process;        
    
    reset <= not rst_n;     
               
               
end architecture RTL;
