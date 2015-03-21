library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity util_spi_master is
    generic (
        CLOCK_FREQUENCY : real;
        SCLK_FREQUENCY  : real;
        
        DATA_BITS : positive);
    port (
        clock  : in std_logic;
        reset  : in std_logic;
        
        data_in  : in std_logic_vector(DATA_BITS-1 downto 0); -- only read when start = '1'
        start    : in std_logic; -- allowed to be set to '1' when busy = '0'
        busy     : out std_logic; -- becomes '1' cycle after start is '1'
        data_out : out std_logic_vector(DATA_BITS-1 downto 0); -- valid when busy = '0'
        
        nSS  : out std_logic := 'Z';
        SCLK : out std_logic := 'Z';
        MOSI : out std_logic := 'Z';
        MISO : in  std_logic);
end util_spi_master;

architecture arc of util_spi_master is
    constant SCLK_HALF_PERIOD_CYCLES : natural := integer(ceil(CLOCK_FREQUENCY/SCLK_FREQUENCY/2.0));
begin
    process (clock) is
        variable countdown : integer range 0 to SCLK_HALF_PERIOD_CYCLES;
        type StateType is (STATE_START, STATE_1, STATE_2, STATE_3, STATE_4);
        variable state : StateType;
        variable shift : std_logic_vector(DATA_BITS-1 downto 0);
        variable shift_out : std_logic_vector(DATA_BITS-1 downto 0);
        variable bit_count : integer range 0 to DATA_BITS-1;
    begin
        if rising_edge(clock) then
            if reset = '1' then
                busy <= '0';
                
                MOSI <= 'Z';
                SCLK <= 'Z';
                nSS <= 'Z';
                state := STATE_START;
                countdown := 0;
            elsif countdown /= 0 then
                countdown := countdown - 1;
            elsif state = STATE_START then
                busy <= '0';
                
                MOSI <= 'Z';
                SCLK <= 'Z';
                nSS <= 'Z';
                if start = '1' then
                    shift := data_in;
                    MOSI <= '0';
                    SCLK <= '0';
                    nSS <= '1';
                    countdown := SCLK_HALF_PERIOD_CYCLES;
                    state := STATE_1;
                    busy <= '1';
                end if;
            elsif state = STATE_1 then
                MOSI <= shift(DATA_BITS-1);
                shift := shift(DATA_BITS-2 downto 0) & "-";
                shift_out := shift_out(DATA_BITS-2 downto 0) & MISO;
                SCLK <= '0';
                nSS <= '0';
                countdown := SCLK_HALF_PERIOD_CYCLES;
                state := STATE_2;
            elsif state = STATE_2 then
                SCLK <= '1';
                countdown := SCLK_HALF_PERIOD_CYCLES;
                if bit_count /= DATA_BITS-1 then
                    STATE := STATE_3;
                else
                    bit_count := bit_count + 1;
                    state := STATE_1;
                end if;
            elsif state = STATE_3 then
                SCLK <= '0';
                countdown := SCLK_HALF_PERIOD_CYCLES;
                state := STATE_4;
            elsif state = STATE_4 then
                nSS <= '1';
                countdown := SCLK_HALF_PERIOD_CYCLES;
                state := STATE_START;
                data_out <= shift_out;
            end if;
        end if;
    end process;
end architecture;
