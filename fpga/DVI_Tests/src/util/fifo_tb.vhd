library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity util_fifo_tb is
    generic (
        LOG_2_DEPTH : natural := 4);
end entity;

architecture arc of util_fifo_tb is
    constant WIDTH : natural := LOG_2_DEPTH + 8;
    
    constant DEPTH : positive := 2**LOG_2_DEPTH - 1; -- XXX - 1 until fifo is able to use all slots at once
    
    signal write_clock  : std_logic := '0';
    signal write_enable : std_logic := '0';
    signal write_data   : std_logic_vector(WIDTH-1 downto 0) := (others => 'U');
    signal write_full   : std_logic;
    
    signal read_clock  : std_logic := '0';
    signal read_enable : std_logic := '0';
    signal read_data   : std_logic_vector(WIDTH-1 downto 0);
    signal read_empty  : std_logic;
begin
    UUT : entity work.util_fifo
        generic map (
            WIDTH => WIDTH,
            LOG_2_DEPTH => LOG_2_DEPTH)
        port map (
            write_clock  => write_clock,
            write_enable => write_enable,
            write_data   => write_data,
            write_full   => write_full,
            
            read_clock  => read_clock,
            read_enable => read_enable,
            read_data   => read_data,
            read_empty  => read_empty);
    
    write_clock <= not write_clock after 3 ns;
    
    read_clock <= not read_clock after 5 ns;
    
    process is
        variable j : integer;
    begin
        wait for 1 us;
        
        assert read_empty = '1' report "read_empty should be 1";
        
        for i in 0 to DEPTH-1 loop
            wait until rising_edge(write_clock);
            assert write_full = '0' report "write was full when it shouldn't have been" severity error;
            write_enable <= '1';
            write_data <= std_logic_vector(to_unsigned(i, WIDTH));
            wait until rising_edge(write_clock);
            write_enable <= '0';
            write_data <= (others => 'U');
            
            wait for 1 us;
            
            assert read_empty = '0' report "read_empty should be 0";
        end loop;
        
        if true then
            wait until rising_edge(write_clock);
            assert write_full = '1' report "write wasn't full when it should have been" severity error;
            write_enable <= '1';
            write_data <= std_logic_vector(to_unsigned(DEPTH, WIDTH));
            wait until rising_edge(write_clock);
            write_enable <= '0';
            write_data <= (others => 'U');
            
            wait for 1 us;
            
            assert read_empty = '0' report "read_empty should be 0";
        end if;
        
        assert write_full = '1';
        
        for i in 0 to DEPTH-1 loop
            wait until rising_edge(read_clock);
            assert read_empty = '0' report "assert read_empty = '0'";
            read_enable <= '1';
            wait until rising_edge(read_clock);
            read_enable <= '0';
            wait until rising_edge(read_clock);
            assert to_integer(unsigned(read_data)) = i report integer'image(to_integer(unsigned(read_data))) & " /= " & integer'image(i);
            
            wait for 1 us;
            
            assert write_full = '0' report "assert write_full = '0'";
        end loop;
        
        assert read_empty = '1' report "assert read_empty = '1'";
        
        wait for 1 us;
        
        j := 0;
        wait until rising_edge(write_clock);
        while true loop
            wait for 1 ns;
            if write_full = '1' then
                exit;
            end if;
            assert write_full = '0' report "write was full when it shouldn't have been" severity error;
            write_enable <= '1';
            write_data <= std_logic_vector(to_unsigned(j, WIDTH));
            wait until rising_edge(write_clock);
            write_enable <= '0';
            write_data <= (others => 'U');
            j := j + 1;
        end loop;
        
        assert j = DEPTH report "assert j = DEPTH";
        
        wait for 1 us;
        
        j := 0;
        wait until rising_edge(read_clock);
        while true loop
            wait for 1 ns;
            if read_empty = '1' then
                exit;
            end if;
            assert read_empty = '0' report "read_empty should be 0";
            read_enable <= '1';
            wait until rising_edge(read_clock);
            read_enable <= '0';
            wait for 1 ns;
            assert to_integer(unsigned(read_data)) = j report integer'image(to_integer(unsigned(read_data))) & " /= " & integer'image(j);
            j := j + 1;
        end loop;
        
        assert j = DEPTH report "assert j = DEPTH";
        
        wait for 1 us;
        
        report "Simulation completed" severity failure;
    end process;
end architecture;
