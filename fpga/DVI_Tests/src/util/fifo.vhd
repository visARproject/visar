library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.util_gray.all;

entity util_fifo is
    generic (
        WIDTH : natural;
        LOG_2_DEPTH : natural);
    port (
        write_clock  : in  std_logic;
        write_enable : in  std_logic;
        write_data   : in  std_logic_vector(WIDTH-1 downto 0);
        write_full   : out std_logic;
        
        read_clock  : in  std_logic;
        read_reset  : in  std_logic := '0'; -- synchronous to read_clock; equivalent to reading all data out
        read_enable : in  std_logic;
        read_data   : out std_logic_vector(WIDTH-1 downto 0);
        read_empty  : out std_logic);
end entity;

architecture arc of util_fifo is
    constant DEPTH : positive := 2**LOG_2_DEPTH;
    
    type BackingType is array (0 to DEPTH-1) of std_logic_vector(WIDTH-1 downto 0); 
    signal backing : BackingType;
    
    signal write_full_s : std_logic := '1';
    signal read_empty_s : std_logic := '1';
    
    signal write_position : unsigned(LOG_2_DEPTH downto 0) := to_unsigned(0, LOG_2_DEPTH+1); -- next position to write to
    signal  read_position : unsigned(LOG_2_DEPTH downto 0) := to_unsigned(0, LOG_2_DEPTH+1); -- next position to read from
    
    signal write_position_gray                       : std_logic_vector(LOG_2_DEPTH downto 0) := binary_to_gray(to_unsigned(0, LOG_2_DEPTH+1));
    signal write_position_gray_read_synchronize_tmp  : std_logic_vector(LOG_2_DEPTH downto 0) := binary_to_gray(to_unsigned(0, LOG_2_DEPTH+1));
    signal write_position_gray_read_synchronized     : std_logic_vector(LOG_2_DEPTH downto 0) := binary_to_gray(to_unsigned(0, LOG_2_DEPTH+1));
    signal  read_position_gray                       : std_logic_vector(LOG_2_DEPTH downto 0) := binary_to_gray(to_unsigned(0, LOG_2_DEPTH+1));
    signal  read_position_gray_write_synchronize_tmp : std_logic_vector(LOG_2_DEPTH downto 0) := binary_to_gray(to_unsigned(0, LOG_2_DEPTH+1));
    signal  read_position_gray_write_synchronized    : std_logic_vector(LOG_2_DEPTH downto 0) := binary_to_gray(to_unsigned(0, LOG_2_DEPTH+1));
begin
    process (write_clock) is
        variable new_write_position : unsigned(LOG_2_DEPTH downto 0);
    begin
        if rising_edge(write_clock) then
            read_position_gray_write_synchronize_tmp <= read_position_gray;
            read_position_gray_write_synchronized <= read_position_gray_write_synchronize_tmp;
            
            new_write_position := write_position;
            if write_enable = '1' and write_full_s = '0' then
                backing(to_integer(write_position(LOG_2_DEPTH-1 downto 0))) <= write_data;
                new_write_position := write_position + 1;
            end if;
            write_position <= new_write_position;
            write_position_gray <= binary_to_gray(new_write_position);
            write_full_s <= '0';
            if read_position_gray_write_synchronized = binary_to_gray(new_write_position + DEPTH) then
                write_full_s <= '1';
            end if;
        end if;
    end process;
    write_full <= write_full_s;
    
    
    process (read_clock) is
        variable new_read_position : unsigned(LOG_2_DEPTH downto 0);
    begin
        if rising_edge(read_clock) then
            write_position_gray_read_synchronize_tmp <= write_position_gray;
            write_position_gray_read_synchronized <= write_position_gray_read_synchronize_tmp;
            
            new_read_position := read_position;
            if read_enable = '1' and read_empty_s = '0' then
                read_data <= backing(to_integer(read_position(LOG_2_DEPTH-1 downto 0)));
                new_read_position := read_position + 1;
            end if;
            if read_reset = '1' then
                new_read_position := gray_to_binary(write_position_gray_read_synchronized);
            end if;
            read_position <= new_read_position;
            read_position_gray <= binary_to_gray(new_read_position);
            read_empty_s <= '0';
            if write_position_gray_read_synchronized = binary_to_gray(new_read_position) then
                read_empty_s <= '1';
            end if;
        end if;
    end process;
    read_empty <= read_empty_s;
end architecture;
