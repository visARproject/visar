library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera.all;
use work.ram_port.all;

entity camera_writer is
    generic (
        BUFFER_ADDRESS : in integer); -- needs to be 4-byte aligned
    port (
        camera_output : in camera_output;
        
        ram_in  : out ram_wr_port_in;
        ram_out : in  ram_wr_port_out);
end entity;

architecture arc of camera_writer is
begin
    process (camera_output) is
        variable dest, next_dest : integer range BUFFER_ADDRESS to BUFFER_ADDRESS + 16#2000000# := BUFFER_ADDRESS;
        variable state, next_state : integer range 0 to 15 := 0;
    begin
        ram_in.cmd.clk <= camera_output.clock;
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        
        ram_in.wr.clk <= camera_output.clock;
        ram_in.wr.en <= '0';
        ram_in.wr.mask <= (others => '-');
        ram_in.wr.data <= (others => '-');
        
        if true then
            ram_in.wr.en <= '1';
            ram_in.wr.mask <= (others => '0');
            ram_in.wr.data <= "0000000" & camera_output.data;
        end if;
        
        if state = 15 then
            ram_in.cmd.en <= '1';
            ram_in.cmd.instr <= WRITE_PRECHARGE_COMMAND;
            ram_in.cmd.bl <= std_logic_vector(to_unsigned(32-1, ram_in.cmd.bl'length));
            ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(dest, ram_in.cmd.byte_addr'length));
            
            next_dest := dest + 16*4;
            next_state := 0;
        else
            next_dest := dest;
            next_state := state + 1;
        end if;
        
        if rising_edge(camera_output.clock) then
            dest := next_dest;
            state := next_state;
        end if;
    end process;
end architecture;
