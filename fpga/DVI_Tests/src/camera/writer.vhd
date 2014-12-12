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
        variable state, next_state : integer range 0 to 3;
        variable state2, next_state2 : integer range 0 to 31;
        variable x, next_x : integer range 0 to CAMERA_WIDTH-1;
        variable y, next_y : integer range 0 to CAMERA_HEIGHT-1;
        variable data, next_data : std_logic_vector(31 downto 0);
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
        
        next_state := state;
        next_state2 := state2;
        next_x := x;
        next_y := y;
        next_data := data;
        
        if camera_output.frame_valid = '0' then
            next_state := 0;
            next_state2 := 0;
            next_x := 0;
            next_y := 0;
        elsif camera_output.data_valid = '1' then
            next_data(8*state+7 downto 8*state) := camera_output.data;
            if x /= CAMERA_WIDTH-1 then
                next_x := x + 1;
            else
                next_x := 0;
                next_y := y + 1;
            end if;
            if state /= 3 then
                next_state := state + 1;
            else
                next_state := 0;
                
                ram_in.wr.en <= '1';
                ram_in.wr.mask <= (others => '0');
                ram_in.wr.data <= next_data;
                
                if state2 /= 31 and x/= CAMERA_WIDTH-1 then
                    next_state2 := state2 + 1;
                else
                    next_state2 := 0;
                    
                    ram_in.cmd.en <= '1';
                    ram_in.cmd.instr <= WRITE_PRECHARGE_COMMAND;
                    ram_in.cmd.bl <= std_logic_vector(to_unsigned(32-1, ram_in.cmd.bl'length));
                    ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(BUFFER_ADDRESS + y * CAMERA_STEP + x/(32*4)*(32*4), ram_in.cmd.byte_addr'length));
                end if;
            end if;
        end if;
        
        if rising_edge(camera_output.clock) then
            state := next_state;
            state2 := next_state2;
            x := next_x;
            y := next_y;
            data := next_data;
        end if;
    end process;
end architecture;
