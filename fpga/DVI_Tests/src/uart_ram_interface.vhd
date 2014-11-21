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
    type CommandStateType is (COMMANDSTATE_IDLE);
    signal commandstate : CommandStateType;
    
    type ReadStateType is (READSTATE_IDLE, READSTATE_GO, READSTATE_GO2, READSTATE_GO3);
    signal readstate : ReadStateType;
    subtype PosType is integer range 0 to DATA_PORT_SIZE/8-1;
    signal pos : PosType;
begin
    ram_in.cmd.clk <= clock;
    ram_in.rd.clk <= clock;
    
    process(clock)
    begin
        if rising_edge(clock) then
            ram_in.cmd.en <= '0';
            
            
            ram_in.rd.en <= '0';
            uart_tx_write <= '0';
            
            if reset = '1' then
                commandstate <= COMMANDSTATE_IDLE;
            elsif commandstate = COMMANDSTATE_IDLE then
                if uart_rx_valid = '1' then
                    if uart_rx_data = x"00" then
                        uart_tx_write <= '1';
                        uart_tx_data <= x"40";
                    else
                        ram_in.cmd.en <= '1';
                        ram_in.cmd.instr <= READ_COMMAND;
                        ram_in.cmd.byte_addr <= std_logic_vector(resize(unsigned(uart_rx_data & "00"), ram_in.cmd.byte_addr'length));
                        ram_in.cmd.bl <= std_logic_vector(to_unsigned(0, ram_in.cmd.bl'length));
                    end if;
                end if;
            end if;
            
            if reset = '1' then
                readstate <= READSTATE_IDLE;
            elsif readstate = READSTATE_IDLE then
                if ram_out.rd.empty = '0' then
                    ram_in.rd.en <= '1';
                    readstate <= READSTATE_GO;
                end if;
            elsif readstate = READSTATE_GO then
                readstate <= READSTATE_GO2;
                pos <= 0;
            elsif readstate = READSTATE_GO2 then
                if uart_tx_ready = '1' then
                    uart_tx_write <= '1';
                    uart_tx_data <= ram_out.rd.data(8*pos+7 downto 8*pos);
                    if pos /= DATA_PORT_SIZE/8-1 then
                        readstate <= READSTATE_GO3;
                        pos <= pos + 1;
                    else
                        readstate <= READSTATE_IDLE;
                    end if;
                end if;
            elsif readstate = READSTATE_GO3 then
                readstate <= READSTATE_GO2;
            end if;
        end if;
    end process;
end architecture;
