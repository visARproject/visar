library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.util_gray.all;

entity util_fifo_narrowed is
    -- data of differing widths is handled big-endian-ishly: a 2-to-1
    -- transfer of "AB" will read as "A" then "B"
    
    -- this simplifies to nothing if WRITE_WIDTH = READ_WIDTH = WIDTH
    
    generic (
        WIDTH : natural;
        LOG_2_DEPTH : natural;
        WRITE_WIDTH : natural;
        READ_WIDTH : natural);
    port (
        write_clock  : in  std_logic;
        write_enable : in  std_logic;
        write_data   : in  std_logic_vector(WRITE_WIDTH-1 downto 0);
        write_full   : out std_logic;
        
        read_clock  : in  std_logic;
        read_enable : in  std_logic;
        read_data   : out std_logic_vector(READ_WIDTH-1 downto 0);
        read_empty  : out std_logic);
end entity;

architecture arc of util_fifo_narrowed is
    constant WRITE_CHUNKS : natural := WIDTH/WRITE_WIDTH;
    signal write_state : integer range 0 to WRITE_CHUNKS-1 := WRITE_CHUNKS-1;
    
    signal fifo_write_enable : std_logic;
    signal fifo_write_data   : std_logic_vector(WIDTH-1 downto 0);
    signal fifo_write_full   : std_logic;
    
    constant READ_CHUNKS : natural := WIDTH/READ_WIDTH;
    signal read_state : integer range 0 to READ_CHUNKS-1 := 0;
    
    signal fifo_read_enable : std_logic;
    signal fifo_read_data   : std_logic_vector(WIDTH-1 downto 0);
    signal fifo_read_empty  : std_logic;
begin
    assert WIDTH mod WRITE_WIDTH = 0 report "WIDTH must be a multiple of WRITE_WIDTH";
    assert WIDTH mod READ_WIDTH = 0 report "WIDTH must be a multiple of READ_WIDTH";
    
    INNER : entity work.util_fifo
        generic map (
            WIDTH => WIDTH,
            LOG_2_DEPTH => LOG_2_DEPTH)
        port map (
            write_clock  => write_clock,
            write_enable => fifo_write_enable,
            write_data   => fifo_write_data,
            write_full   => fifo_write_full,
            
            read_clock => read_clock,
            read_enable => fifo_read_enable,
            read_data => fifo_read_data,
            read_empty => fifo_read_empty);
    
    process (fifo_write_full, write_state, write_enable, write_data, write_clock) is
    begin
        write_full <= '0';
        fifo_write_enable <= '0';
        fifo_write_data(WRITE_WIDTH*(0+1)-1 downto WRITE_WIDTH*0) <= (others => 'U'); -- prevent inferring latches
        if write_state /= 0 then
            if write_enable = '1' then
                if rising_edge(write_clock) then
                    fifo_write_data(WRITE_WIDTH*(write_state+1)-1 downto WRITE_WIDTH*write_state) <= write_data;
                    write_state <= 0;
                end if;
            end if;
        else
            if fifo_write_full = '1' then
                write_full <= '1';
            else
                if write_enable = '1' then
                    fifo_write_data(WRITE_WIDTH*(write_state+1)-1 downto WRITE_WIDTH*write_state) <= write_data;
                    fifo_write_enable <= '1';
                    if rising_edge(write_clock) then
                        write_state <= WRITE_CHUNKS-1;
                    end if;
                end if;
            end if;
        end if;
    end process;
    
    process (fifo_read_data, read_state, read_enable, read_clock, fifo_read_empty) is
    begin
        read_empty <= '0';
        fifo_read_enable <= '0';
        read_data <= fifo_read_data(READ_WIDTH*(read_state+1)-1 downto READ_WIDTH*read_state);
        if read_state /= 0 then
            if read_enable = '1' then
                if rising_edge(read_clock) then
                    read_state <= read_state - 1;
                end if;
            end if;
        else
            if fifo_read_empty = '1' then
                read_empty <= '1';
            else
                if read_enable = '1' then
                    fifo_read_enable <= '1';
                    if rising_edge(read_clock) then
                        read_state <= READ_CHUNKS - 1;
                    end if;
                end if;
            end if;
        end if;
    end process;
end architecture;
