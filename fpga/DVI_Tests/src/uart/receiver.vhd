library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity uart_receiver is
    generic (
        DATA_BITS : natural := 8;
        STOP_BITS : natural := 1;
        CLOCK_FREQUENCY : real;
        BAUD_RATE : real);
    port (
        clock : in std_logic;
        reset : in std_logic;
        
        rx : in std_logic;
        
        valid : out std_logic;
        data : out std_logic_vector(DATA_BITS-1 downto 0));
end entity;

architecture arc of uart_receiver is
    signal rx_sync1, rx_sync2, rx_sync3 : std_logic;
    
    
    type state_t is (STATE_IDLE, STATE_RUNNING);
    signal state : state_t;
    
    signal data_int : std_logic_vector(1+DATA_BITS+STOP_BITS-1 downto 0);
    constant STOP_DATA : std_logic_vector(STOP_BITS-1 downto 0) := (others => '1');
    
    subtype pos_t is integer range 0 to
        integer(round(CLOCK_FREQUENCY/BAUD_RATE*(real(data_int'length)-1.0+0.5)))+1;
    signal pos : pos_t;
begin
    process(clock)
    begin
        if rising_edge(clock) then
            valid <= '0';
            
            rx_sync1 <= rx;
            rx_sync2 <= rx_sync1;
            rx_sync3 <= rx_sync2;
            
            if reset = '1' then
                state <= STATE_IDLE;
            elsif state = STATE_IDLE then
                if rx_sync3 = '1' and rx_sync2 = '0' then
                    state <= STATE_RUNNING;
                    pos <= 0;
                end if;
            else -- state = STATE_RUNNING
                for i in 0 to data_int'length-1 loop
                    if pos = integer(round(CLOCK_FREQUENCY/BAUD_RATE*(real(i)+0.5))) then
                        data_int(i) <= rx_sync3;
                    end if;
                end loop;
                if pos = integer(round(CLOCK_FREQUENCY/BAUD_RATE*(real(data_int'length)-1.0+0.5)))+1 then
                    state <= STATE_IDLE;
                    if data_int(0) = '0' and data_int(data_int'length-1 downto data_int'length-STOP_BITS) = STOP_DATA then
                        valid <= '1';
                        data <= data_int(DATA_BITS downto 1);
                    end if;
                else
                    pos <= pos + 1;
                end if;
            end if;
        end if;
    end process;
end architecture arc;
