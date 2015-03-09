library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity util_fifo_fallthrough is
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

architecture arc of util_fifo_fallthrough is
    signal fifo_read_enable : std_logic;
    signal fifo_read_empty : std_logic;
    
    signal have_data : std_logic := '0';
begin
    INNER : entity work.util_fifo_narrowed
        generic map (
            WIDTH => WIDTH,
            LOG_2_DEPTH => LOG_2_DEPTH,
            WRITE_WIDTH => WRITE_WIDTH,
            READ_WIDTH => READ_WIDTH)
        port map (
            write_clock  => write_clock,
            write_enable => write_enable,
            write_data   => write_data,
            write_full   => write_full,
            
            read_clock => read_clock,
            read_enable => fifo_read_enable,
            read_data => read_data,
            read_empty => fifo_read_empty);
    
    process (fifo_read_empty, have_data, read_enable, read_clock) is
    begin
        fifo_read_enable <= '0';
        if fifo_read_empty = '0' and have_data = '0' then
            fifo_read_enable <= '1';
        elsif read_enable = '1' and have_data = '1' then
            if fifo_read_empty = '0' then
                fifo_read_enable <= '1';
            else
            end if;
        end if;
        if rising_edge(read_clock) then
            if fifo_read_empty = '0' and have_data = '0' then
                have_data <= '1';
            elsif read_enable = '1' and have_data = '1' then
                if fifo_read_empty = '0' then
                else
                    have_data <= '0';
                end if;
            end if;
        end if;
    end process;
    
    read_empty <= not have_data;
end architecture;
