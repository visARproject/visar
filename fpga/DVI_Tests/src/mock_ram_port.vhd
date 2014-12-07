library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;

entity mock_ram_port is
    port (
        ram_in  : in  ram_rd_port_in;
        ram_out : out ram_rd_port_out);
end;

architecture arc of mock_ram_port is
    signal memory : MemoryType(0 to 2048-1);
    constant FIFO_SIZE : positive := 64;
    constant DATA_WIDTH : positive := 32;
    type FIFOBackingType is array (0 to FIFO_SIZE-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
    signal fifo_backing : FIFOBackingType;
    signal fifo_read_position, fifo_write_position : integer := 0;
begin
    process
    begin
        for i in 0 to 255 loop
            memory(1230 + i) <= std_logic_vector(to_unsigned(i, 8));
        end loop;
        memory(1236) <= "00000000";
        memory(1237) <= "00000000";
        memory(1238) <= "10000000";
        memory(1239) <= "00011101";
        memory(1240) <= "01000001";
        memory(1241) <= "00000100";
        memory(1242) <= "00000000";
        memory(1243) <= "00000000";
        memory(1244) <= "00000000";
        memory(1245) <= "00000000";
        memory(1246) <= "00000000";
        memory(1247) <= "11000000";
        memory(1248) <= "00100011";
        memory(1249) <= "11101111";
        memory(1250) <= "00000000";
        memory(1251) <= "00000000";
        memory(1252) <= "00000000";
        memory(1253) <= "00000000";
        memory(1254) <= "00000000";
        memory(1255) <= "00000000";
        
        wait;
    end process;
    
    process (ram_in.cmd.clk) is
    begin
        if rising_edge(ram_in.cmd.clk) and ram_in.cmd.en = '1' then
            assert ram_in.cmd.instr = READ_PRECHARGE_COMMAND;
            for i in 0 to to_integer(unsigned(ram_in.cmd.bl)) + 1 - 1 loop
                for j in 0 to 3 loop
                    fifo_backing(fifo_write_position + i mod FIFO_SIZE)(8*j+7 downto 8*j) <= memory(to_integer(unsigned(ram_in.cmd.byte_addr)) + i*4 + j);
                end loop;
            end loop;
            fifo_write_position <= fifo_write_position + to_integer(unsigned(ram_in.cmd.bl)) + 1;
        end if;
    end process;
    
    ram_out.rd.data <= fifo_backing(fifo_read_position mod FIFO_SIZE);
    ram_out.rd.empty <= '1' when fifo_read_position = fifo_write_position else '0';
    
    process (ram_in.rd.clk) is
    begin
        if rising_edge(ram_in.rd.clk) and ram_in.rd.en = '1' and fifo_read_position /= fifo_write_position then
            fifo_read_position <= fifo_read_position + 1;
        end if;
    end process;
end arc;
