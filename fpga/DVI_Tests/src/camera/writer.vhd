library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera_pkg.all;
use work.ram_port.all;

entity camera_writer is
    generic (
        BUFFER_ADDRESS : integer); -- needs to be 4-byte aligned
    port (
        camera_output : in camera_output;
        
        ram_in  : out ram_wr_port_in;
        ram_out : in  ram_wr_port_out);
end entity;

architecture arc of camera_writer is
    constant BURST_LENGTH : integer := RAM_FIFO_LENGTH/4;
begin
    process (camera_output, ram_out) is
        variable state, next_state : integer range 0 to 2 := 0;
        variable words_committed, next_words_committed, words_committed_ideal, next_words_committed_ideal : integer range 0 to BURST_LENGTH := 0;
        variable last_pixel1, next_last_pixel1, last_pixel2, next_last_pixel2 : unsigned(9 downto 0);
        variable dest, next_dest : integer range 0 to 32*1024*1024-1 := 0;
        variable dest2, next_dest2 : integer range 0 to 32*1024*1024-1 := 0;
        variable bad_write, next_bad_write : boolean;
    begin
        ram_in.cmd.clk <= camera_output.clock;
        ram_in.wr.clk <= camera_output.clock;
        
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        
        ram_in.wr.en <= '0';
        ram_in.wr.mask <= (others => '-');
        ram_in.wr.data <= (others => '-');
        
        next_state := state;
        next_words_committed := words_committed;
        next_words_committed_ideal := words_committed_ideal;
        next_last_pixel1 := last_pixel1;
        next_last_pixel2 := last_pixel2;
        next_dest := dest;
        next_dest2 := dest2;
        next_bad_write := bad_write;
        
        if camera_output.data_valid = '1' then
            -- 3 input words (of 2 pixels each) turns into 2 output words (of 32 (30 used) bits each)
            if state = 0 then
                next_state := 1;
                if camera_output.last_column = '1' then
                    if ram_out.wr.full = '0' and not bad_write then
                        ram_in.wr.en <= '1';
                        ram_in.wr.mask <= (others => '0');
                        ram_in.wr.data <= "00" & "1111111111" & std_logic_vector(camera_output.pixel2) & std_logic_vector(camera_output.pixel1);
                        next_words_committed := words_committed + 1;
                    else
                        next_bad_write := true;
                    end if;
                    next_words_committed_ideal := words_committed_ideal + 1;
                end if;
            elsif state = 1 then
                if ram_out.wr.full = '0' and not bad_write then
                    ram_in.wr.en <= '1';
                    ram_in.wr.mask <= (others => '0');
                    ram_in.wr.data <= "00" & std_logic_vector(camera_output.pixel1) & std_logic_vector(last_pixel2) & std_logic_vector(last_pixel1);
                    next_words_committed := words_committed + 1;
                else
                    next_bad_write := true;
                end if;
                next_words_committed_ideal := words_committed_ideal + 1;
                next_state := 2;
            else
                if ram_out.wr.full = '0' and not bad_write then
                    ram_in.wr.en <= '1';
                    ram_in.wr.mask <= (others => '0');
                    ram_in.wr.data <= "00" & std_logic_vector(camera_output.pixel2) & std_logic_vector(camera_output.pixel1) & std_logic_vector(last_pixel2);
                    next_words_committed := words_committed + 1;
                else
                    next_bad_write := true;
                end if;
                next_words_committed_ideal := words_committed_ideal + 1;
                next_state := 0;
            end if;
            
            
            
            next_last_pixel1 := camera_output.pixel1;
            next_last_pixel2 := camera_output.pixel2;
            
            if next_words_committed_ideal = BURST_LENGTH or camera_output.last_column = '1' then
                if next_words_committed /= 0 then
                    ram_in.cmd.en <= '1';
                    ram_in.cmd.instr <= WRITE_PRECHARGE_COMMAND;
                    ram_in.cmd.bl <= std_logic_vector(to_unsigned(next_words_committed-1, ram_in.cmd.bl'length));
                    ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(BUFFER_ADDRESS + dest2, ram_in.cmd.byte_addr'length));
                end if;
                
                next_dest2 := dest2 + 4 * next_words_committed_ideal;
                next_words_committed := 0;
                next_words_committed_ideal := 0;
                next_bad_write := false;
            end if;
            
            if camera_output.last_column = '1' then
                next_state := 0;
                next_dest := dest + CAMERA_STEP; -- XXX should be (CAMERA_STEP/2+2)/3*8 ... or something
                next_dest2 := dest + CAMERA_STEP;
            end if;
            
            if camera_output.last_pixel = '1' then
                next_state := 0;
                next_dest := 0;
                next_dest2 := 0;
            end if;
        end if;
        
        if rising_edge(camera_output.clock) then
            state := next_state;
            words_committed := next_words_committed;
            words_committed_ideal := next_words_committed_ideal;
            last_pixel1 := next_last_pixel1;
            last_pixel2 := next_last_pixel2;
            dest := next_dest;
            dest2 := next_dest2;
            bad_write := next_bad_write;
        end if;
    end process;
end architecture;
