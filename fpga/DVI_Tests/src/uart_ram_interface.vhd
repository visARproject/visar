library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;

entity uart_ram_interface is
    port (
        clock : in std_logic;
        reset : in std_logic;
        
        ram_in  : out ram_bidir_port_in;
        ram_out : in  ram_bidir_port_out;
        
        uart_tx_ready : in  std_logic;
        uart_tx_data  : out std_logic_vector(7 downto 0);
        uart_tx_write : out std_logic;
        
        uart_rx_valid : in std_logic;
        uart_rx_data  : in std_logic_vector(7 downto 0);
        
        pair7P:  inout std_logic;
        pair7N:  inout std_logic;
        pair8P:  inout std_logic;
        pair8N:  inout std_logic;
        pair9P:  inout std_logic;
        pair9N:  inout std_logic;
        pair12P: inout std_logic;
        pair12N: inout std_logic;
        pair13P: inout std_logic;
        pair13N: inout std_logic;
        pair14P: inout std_logic;
        pair14N: inout std_logic);
end entity;

architecture arc of uart_ram_interface is
    signal debug_in : std_logic_vector(31 downto 0);
    signal debug_out : std_logic_vector(31 downto 0);
    signal debug_en : std_logic_vector(31 downto 0) := (others => '0');
    signal debug_real_out : std_logic_vector(31 downto 0);
begin
    process (debug_out, debug_en) is
    begin
        for i in 0 to 31 loop
            if debug_en(i) = '1' then
                debug_real_out(i) <= debug_out(i);
            else
                debug_real_out(i) <= 'Z';
            end if;
        end loop;
    end process;
    
    pair7P  <= debug_real_out( 0);
    pair7N  <= debug_real_out( 1);
    pair8P  <= debug_real_out( 2);
    pair8N  <= debug_real_out( 3);
    pair9P  <= debug_real_out( 4);
    pair9N  <= debug_real_out( 5);
    pair12P <= debug_real_out( 6);
    pair12N <= debug_real_out( 7);
    pair13P <= debug_real_out( 8);
    pair13N <= debug_real_out( 9);
    pair14P <= debug_real_out(10);
    pair14N <= debug_real_out(11);
    
    debug_in <= "00000000000000000000" & pair14N & pair14P & pair13N & pair13P & pair12N & pair12P & pair9N & pair9P & pair8N & pair8P & pair7N & pair7P;
    
    process(clock, reset, uart_rx_valid, uart_rx_data, debug_in)
        type StateType is (IDLE, READ, EXEC);
        variable state, next_state : StateType;
        variable pos, next_pos : integer range 0 to 8;
        variable command, next_command : std_logic_vector(71 downto 0);
    begin
        ram_in.cmd.clk <= clock;
        ram_in.wr.clk <= clock;
        
        next_state := state;
        next_pos := pos;
        next_command := command;
        
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        ram_in.wr.en <= '0';
        ram_in.wr.data <= (others => '-');
        ram_in.wr.mask <= (others => '-');
        
        if reset = '1' then
            next_state := IDLE;
        elsif state = IDLE then
            if uart_rx_valid = '1' and uart_rx_data = x"da" then
                next_pos := 0;
                next_state := READ;
            end if;
        elsif state = READ then
            if uart_rx_valid = '1' then
                next_command(8*pos+7 downto 8*pos) := uart_rx_data;
                if pos /= 8 then
                    next_pos := pos + 1;
                else
                    if next_command(7 downto 0) = x"00" then -- read
                    else
                        ram_in.wr.en <= '1';
                        if command(39 downto 8) = x"FFFFFFFC" then
                            ram_in.wr.data <= debug_in;
                        else
                            ram_in.wr.data <= next_command(71 downto 40);
                        end if;
                        ram_in.wr.mask <= (others => '0');
                    end if;
                    next_state := EXEC;
                end if;
            end if;
        elsif state = EXEC then
            ram_in.cmd.en <= '1';
            if command(7 downto 0) = x"00" then -- read
                ram_in.cmd.instr <= READ_PRECHARGE_COMMAND;
            else
                ram_in.cmd.instr <= WRITE_PRECHARGE_COMMAND;
            end if;
            ram_in.cmd.byte_addr <= command(37 downto 8);
            ram_in.cmd.bl <= std_logic_vector(to_unsigned(0, ram_in.cmd.bl'length));
            next_state := IDLE;
        end if;
        
        if rising_edge(clock) then
            if state = EXEC and command(39 downto 8) = x"FFFFFFF4" and command(7 downto 0) /= x"00" then
                debug_out <= command(71 downto 40);
            end if;
            if state = EXEC and command(39 downto 8) = x"FFFFFFF8" and command(7 downto 0) /= x"00" then
                debug_en <= command(71 downto 40);
            end if;
            state := next_state;
            pos := next_pos;
            command := next_command;
        end if;
    end process;
    
    process(clock, reset, ram_out, uart_tx_ready)
        type ReadStateType is (READSTATE_IDLE, READSTATE_GO);
        variable state, next_state : ReadStateType;
        variable pos, next_pos : integer range 0 to DATA_PORT_SIZE/8-1;
    begin
        ram_in.rd.clk <= clock;
        
        next_state := state;
        next_pos := pos;
        
        ram_in.rd.en <= '0';
        uart_tx_write <= '0';
        uart_tx_data <= (others => '-');
        
        if reset = '1' then
            next_state := READSTATE_IDLE;
        elsif state = READSTATE_IDLE then
            if ram_out.rd.empty = '0' then
                next_pos := 0;
                next_state := READSTATE_GO;
            end if;
        elsif state = READSTATE_GO then
            if uart_tx_ready = '1' then
                uart_tx_write <= '1';
                uart_tx_data <= ram_out.rd.data(8*pos+7 downto 8*pos);
                if pos /= DATA_PORT_SIZE/8-1 then
                    next_pos := pos + 1;
                else
                    next_state := READSTATE_IDLE;
                ram_in.rd.en <= '1';
                end if;
            end if;
        end if;
        
        if rising_edge(clock) then
            state := next_state;
            pos := next_pos;
        end if;
    end process;
end architecture;
