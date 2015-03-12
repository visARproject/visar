library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity util_fifo_fallthrough_tb is
    generic (
        LOG_2_DEPTH : natural := 4);
end entity;

architecture arc of util_fifo_fallthrough_tb is
    constant WIDTH : natural := 32;
    
    constant APPROXIMATE_DEPTH : positive := 2**LOG_2_DEPTH;
    
    signal write_clock  : std_logic := '0';
    signal write_enable : std_logic := '0';
    signal write_data   : std_logic_vector(2*WIDTH-1 downto 0) := (others => 'U');
    signal write_full   : std_logic;
    
    signal read_clock  : std_logic := '0';
    signal read_enable : std_logic := '0';
    signal read_data   : std_logic_vector(WIDTH-1 downto 0);
    signal read_empty  : std_logic;
    
    signal start_external_read : boolean := false;
    shared variable words_read : integer := 0;
begin
    UUT : entity work.util_fifo_fallthrough
        generic map (
            WIDTH => 8*WIDTH,
            LOG_2_DEPTH => LOG_2_DEPTH-1,
            WRITE_WIDTH => 2*WIDTH,
            READ_WIDTH => WIDTH)
        port map (
            write_clock  => write_clock,
            write_enable => write_enable,
            write_data   => write_data,
            write_full   => write_full,
            
            read_clock  => read_clock,
            read_enable => read_enable,
            read_data   => read_data,
            read_empty  => read_empty);
    
    write_clock <= not write_clock after 3000 ps;
    
    read_clock <= not read_clock after 5119 ps;
    
    process is
        variable words_written : integer := 0;
        variable seed1 : integer := 9;
        variable seed2 : integer := 3;
        variable rand : real;
    begin
        wait for 1 us;
        
        -- fill fifo completely
        while true loop
            wait until falling_edge(write_clock);
            write_enable <= '0';
            if write_full = '1' then
                exit;
            end if;
            write_enable <= '1';
            write_data <= std_logic_vector(to_unsigned(words_written + 10, WIDTH)) & std_logic_vector(to_unsigned(words_written + 10 + 1, WIDTH));
            words_written := words_written + 2;
        end loop;
        
        report integer'image(words_written) & " words written (should be around " & integer'image(APPROXIMATE_DEPTH) & ")";
        
        wait for 1 us;
        
        while true loop
            wait until falling_edge(read_clock);
            if read_empty = '1' then
                exit;
            end if;
            assert to_integer(unsigned(read_data)) = words_read + 10 report "read_data mismatch (" & integer'image(to_integer(unsigned(read_data))) & " /= " & integer'image(words_read + 10) & ")";
            read_enable <= '1';
            words_read := words_read + 1;
        end loop;
        read_enable <= 'L';
        report integer'image(words_read) & " words read (should be around " & integer'image(APPROXIMATE_DEPTH) & ")";
        
        wait for 1 us;
        
        start_external_read <= true;
        
        wait for 1 us;
        
        while true loop
            uniform(seed1, seed2, rand);
            if words_written mod 1000 > 500 then
                wait for rand * 50 ns;
            else
                wait for rand * 200 ns;
            end if;
            wait until falling_edge(write_clock);
            write_enable <= '0';
            if write_full = '1' then
                next;
            end if;
            write_enable <= '1';
            write_data <= std_logic_vector(to_unsigned(words_written + 10, WIDTH)) & std_logic_vector(to_unsigned(words_written + 10 + 1, WIDTH));
            words_written := words_written + 2;
            wait until falling_edge(write_clock);
            write_enable <= '0';
        end loop;
    end process;
    
    process is
        variable seed1 : integer := 1;
        variable seed2 : integer := 2;
        variable rand : real;
    begin
        read_enable <= 'L';
        wait until start_external_read;
        
        while true loop
            uniform(seed1, seed2, rand); wait for rand * 50 ns;
            wait until falling_edge(read_clock);
            if read_empty = '1' then
                next;
            end if;
            assert to_integer(unsigned(read_data)) = words_read + 10 report "read_data mismatch (" & integer'image(to_integer(unsigned(read_data))) & " /= " & integer'image(words_read + 10) & ")";
            words_read := words_read + 1;
            read_enable <= '1';
            wait until falling_edge(read_clock);
            read_enable <= 'L';
        end loop;
    end process;
end architecture;
