library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity uart_transmitter is
    generic (
        DATA_BITS : natural := 8;
        STOP_BITS : natural := 2;
        CLOCK_FREQUENCY : real;
        BAUD_RATE : real);
    port (
        clock : in std_logic; -- frequency should be baud rate
        reset : in std_logic;
        
        tx : out std_logic;
        
        ready : out std_logic; -- write is allowed on next clock edge
        data : in std_logic_vector(DATA_BITS-1 downto 0);
        write : in std_logic);
end entity;

architecture arc of uart_transmitter is
    signal real_reset : std_logic;
    
    type state_t is (STATE_IDLE, STATE_RUNNING);
    signal state : state_t;
    
    signal data_int : std_logic_vector(1+DATA_BITS+STOP_BITS-1 downto 0);
    constant STOP_DATA : std_logic_vector(STOP_BITS-1 downto 0) := (others => '1');
    
    subtype pos_t is integer range 0 to integer(round(CLOCK_FREQUENCY/BAUD_RATE*real(data_int'length)));
    signal pos : pos_t;
begin
    U_reset_gen : entity work.reset_gen
        port map (
            clock => clock,
            reset_in => reset,
            reset_out => real_reset);
    
    process(clock)
    begin
        if rising_edge(clock) then
            ready <= '0';
            
            if real_reset = '1' then
                state <= STATE_IDLE;
                tx <= '1';
            elsif state = STATE_IDLE then
                tx <= '1';
                if write = '1' then
                    state <= STATE_RUNNING;
                    data_int <= STOP_DATA & data & '0';
                    pos <= 0;
                else
                    ready <= '1';
                end if;
            else -- state = STATE_RUNNING
                for i in 0 to data_int'length-1 loop
                    if pos = integer(round(CLOCK_FREQUENCY/BAUD_RATE*real(i))) then
                        tx <= data_int(i);
                    end if;
                end loop;
                if pos = integer(round(CLOCK_FREQUENCY/BAUD_RATE*real(data_int'length))) then
                    state <= STATE_IDLE;
                else
                    pos <= pos + 1;
                end if;
            end if;
        end if;
    end process;
end architecture arc;
