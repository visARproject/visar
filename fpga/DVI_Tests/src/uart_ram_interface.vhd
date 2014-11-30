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
        uart_rx_data  : in std_logic_vector(7 downto 0));
end entity;

architecture arc of uart_ram_interface is
begin
    process(clock, reset, uart_rx_valid, uart_rx_data)
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
                        ram_in.wr.data <= next_command(71 downto 40);
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
