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
        
        inhibit : in std_logic;
        
        ram_in  : out ram_wr_port_in;
        ram_out : in  ram_wr_port_out);
end entity;

architecture arc of camera_writer is
    constant BURST_LENGTH : integer := 32;
begin
    process (camera_output, inhibit) is
        variable dest, next_dest : integer range 0 to 32*1024*1024-1 := 0;
        variable state, next_state : integer range 0 to BURST_LENGTH-1 := 0;
        variable real_inhibit : std_logic;
        variable inhibit1, inhibit2 : std_logic;
        variable count : unsigned(6 downto 0);
    begin
        if rising_edge(camera_output.clock) then
            dest := next_dest;
            state := next_state;
            
            inhibit2 := inhibit1;
            inhibit1 := inhibit;
            
            count := count + 1;
        end if;
        
        if dest >= 31*1024*1024 and inhibit2 = '1' then
            real_inhibit := '1';
        else
            real_inhibit := '0';
        end if;
        
        
        ram_in.cmd.clk <= camera_output.clock;
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        
        ram_in.wr.clk <= camera_output.clock;
        ram_in.wr.en <= '0';
        ram_in.wr.mask <= (others => '-');
        ram_in.wr.data <= (others => '-');
        
        next_dest := dest;
        next_state := state;
        
        if real_inhibit = '0' then
            if true then
                ram_in.wr.en <= '1';
                ram_in.wr.mask <= (others => '0');
                ram_in.wr.data <= std_logic_vector(count) & camera_output.data;
            end if;
            
            if state = BURST_LENGTH-1 then
                ram_in.cmd.en <= '1';
                ram_in.cmd.instr <= WRITE_PRECHARGE_COMMAND;
                ram_in.cmd.bl <= std_logic_vector(to_unsigned(BURST_LENGTH-1, ram_in.cmd.bl'length));
                ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(BUFFER_ADDRESS + dest, ram_in.cmd.byte_addr'length));
                
                if dest + BURST_LENGTH*4 >= 32*1024*1024 then
                    next_dest := 0;
                else
                    next_dest := dest + BURST_LENGTH*4;
                end if;
                next_state := 0;
            else
                next_state := state + 1;
            end if;
        end if;
    end process;
end architecture;
