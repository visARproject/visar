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
    constant BURST_LENGTH : integer := 16;
begin
    process (camera_output.clock) is
        variable state : integer range 0 to 2 := 0;
        variable words_committed : integer range 0 to BURST_LENGTH := 0;
        variable last_pixel1, last_pixel2 : unsigned(9 downto 0);
        variable dest : integer range 0 to 32*1024*1024-1 := 0;
        variable dest2 : integer range 0 to 32*1024*1024-1 := 0;
    begin
        ram_in.cmd.clk <= camera_output.clock;
        ram_in.wr.clk <= camera_output.clock;
        if rising_edge(camera_output.clock) then
            ram_in.cmd.en <= '0';
            ram_in.cmd.instr <= (others => '-');
            ram_in.cmd.bl <= (others => '-');
            ram_in.cmd.byte_addr <= (others => '-');
            
            ram_in.wr.en <= '0';
            ram_in.wr.mask <= (others => '-');
            ram_in.wr.data <= (others => '-');
            
            if camera_output.data_valid = '1' then
                -- 3 input words (of 2 pixels each) turns into 2 output words (of 32 (30 used) bits each)
                if state = 0 then
                    state := 1;
                    if camera_output.last_column = '1' then
                        ram_in.wr.en <= '1';
                        ram_in.wr.mask <= (others => '0');
                        ram_in.wr.data <= "00" & "1111111111" & std_logic_vector(camera_output.pixel2) & std_logic_vector(camera_output.pixel1);
                        words_committed := words_committed + 1;
                    end if;
                elsif state = 1 then
                    ram_in.wr.en <= '1';
                    ram_in.wr.mask <= (others => '0');
                    ram_in.wr.data <= "00" & std_logic_vector(camera_output.pixel1) & std_logic_vector(last_pixel2) & std_logic_vector(last_pixel1);
                    words_committed := words_committed + 1;
                    state := 2;
                    -- XXX if last_column happens here, one pixel (camera_output.pixel2) is lost!
                else
                    ram_in.wr.en <= '1';
                    ram_in.wr.mask <= (others => '0');
                    ram_in.wr.data <= "00" & std_logic_vector(camera_output.pixel2) & std_logic_vector(camera_output.pixel1) & std_logic_vector(last_pixel2);
                    words_committed := words_committed + 1;
                    state := 0;
                end if;
                
                last_pixel1 := camera_output.pixel1;
                last_pixel2 := camera_output.pixel2;
                
                if words_committed = BURST_LENGTH or camera_output.last_column = '1' then
                    ram_in.cmd.en <= '1';
                    ram_in.cmd.instr <= WRITE_PRECHARGE_COMMAND;
                    ram_in.cmd.bl <= std_logic_vector(to_unsigned(words_committed-1, ram_in.cmd.bl'length));
                    ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(BUFFER_ADDRESS + dest2, ram_in.cmd.byte_addr'length));
                    
                    dest2 := dest2 + 4 * words_committed;
                    words_committed := 0;
                end if;
                
                if camera_output.last_column = '1' then
                    state := 0;
                    dest := dest + CAMERA_STEP; -- XXX should be (CAMERA_STEP/2+2)/3*8 ... or something
                    dest2 := dest;
                end if;
                
                if camera_output.last_pixel = '1' then
                    state := 0;
                    dest := 0;
                    dest2 := dest;
                end if;
            end if;
        end if;
    end process;
end architecture;
