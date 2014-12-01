library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera_pkg.all;

entity video_distorter_map_decoder is
    generic (
        memory_location : integer); -- needs to be 4-byte aligned
    port (
        ram_in  : out ram_rd_port_in;
        ram_out : in  ram_rd_port_out;
        
        clock  : in  std_logic;
        reset  : in  std_logic; -- must be asserted for "a while"
        en     : in  std_logic; -- acts like a normal FIFO - en is needed for first read; must not be asserted for "a while" after reset
        output : out CameraTripleCoordinate);
end entity;

architecture arc of video_distorter_map_decoder is
    constant N : integer := 2**5;
    constant SIZE : integer := N+1;
    
    type CameraInterpolationCoordinate is record
        x : integer range 0 to 2*CAMERA_WIDTH*N-1; -- stacked left-right because distorter buffer moves left-right
        y : integer range 0 to CAMERA_HEIGHT*N-1;
    end record;
    
    type CameraTripleCoordinate is record
        red   : CameraInterpolationCoordinate;
        green : CameraInterpolationCoordinate;
        blue  : CameraInterpolationCoordinate;
    end record;
begin
    process (ram_in, clock, en) is
        variable state, next_state : (STATE_START);
        variable current, current2 : std_logic_vector(32*5-1 downto 0);
        variable current_loaded, next_current_loaded, current2_loaded, next_current2_loaded : std_logic;
        variable current2_load_pos, next_current2_load_pos : integer range 0 to 4;
        variable first : CameraTripleCoordinate;
        variable last  : CameraTripleCoordinate;
        variable fifo_count, next_fifo_count : integer range 0 to 100;
        variable pos, next_pos : integer range 0 to SIZE-1;
        variable mem_pos, next_mem_pos : integer range memory_location to memory_location+2**27-1;
        constant READ_BURST_LENGTH_WORDS : integer := 32;
    begin
        ram_in.cmd.clk <= clock;
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        
        ram_in.rd.clk <= clock;
        ram_in.rd.en <= '0';
        
        next_state := state;
        next_fifo_count := fifo_count;
        
        if reset = '1' then
            next_state := STATE_START;
            next_current_loaded := '0';
            next_next_loaded := '0';
            next_fifo_count := 0;
            next_pos := SIZE-1;
            next_mem_pos := memory_location;
            
            ram_in.rd.en <= '1';
        else
            if en = '1' then
                if pos /= SIZE-1 then
                    -- increment and output new result
                else
                    next_current := current2;
                    next_current2_loaded := '0';
                end if;
            end if;
            
            -- keep current2 loaded
            if next_current2_loaded = '0' and ram_in.rd.empty = '0' then
                current2(current2_load_pos*32+31 downto current2_load_pos*32) := ram_in.rd.data;
                ram_in.rd.en <= '1';
                next_fifo_count := fifo_count - 1;
                if current2_load_pos /= 4 then
                    next_current2_load_pos := current2_load_pos + 1;
                else
                    next_current2_loaded := '1';
                end if;
            end if;
            
            -- keep RAM read FIFO filled
            if next_fifo_count <= RAM_FIFO_LENGTH - READ_BURST_LENGTH then
                ram_in.cmd.en <= '1';
                ram_in.cmd.instr <= READ_PRECHARGE_COMMAND;
                ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(mem_pos, ram_in.cmd.byte_addr'length));
                ram_in.cmd.bl <= std_logic_vector(to_unsigned(READ_BURST_LENGTH_WORDS - 1, ram_in.cmd.bl'length));
                
                next_fifo_count := next_fifo_count + READ_BURST_LENGTH_WORDS;
                next_mem_pos := mem_pos + READ_BURST_LENGTH_WORDS * 4;
            end if;
        end if;
        
        first.red  .x <= to_integer(unsigned(current( 12-1 downto   0)));
        first.red  .y <= to_integer(unsigned(current( 23-1 downto  12)));
        first.green.x <= to_integer(unsigned(current( 35-1 downto  23)));
        first.green.y <= to_integer(unsigned(current( 46-1 downto  35)));
        first.blue .x <= to_integer(unsigned(current( 58-1 downto  46)));
        first.blue .y <= to_integer(unsigned(current( 69-1 downto  58)));
        
        last .red  .x <= to_integer(unsigned(current( 81-1 downto  69)));
        last .red  .y <= to_integer(unsigned(current( 92-1 downto  81)));
        last .green.x <= to_integer(unsigned(current(104-1 downto  92)));
        last .green.y <= to_integer(unsigned(current(115-1 downto 104)));
        last .blue .x <= to_integer(unsigned(current(127-1 downto 115)));
        last .blue .y <= to_integer(unsigned(current(138-1 downto 127)));
        
        green_tmp.x
        green_tmp.y <= to_integer(unsigned(data(23 downto 12)));
        
        output.green <= green_tmp;
        
        --red.x <= green_tmp.x + to_integer(unsigned(data));
        --red.y <= green_tmp.x + to_integer(unsigned(data));
        output.red <= green_tmp; -- XXX
        
        output.blue <= green_tmp; -- XXX
        
        if rising_edge(clock) then
            state := next_state;
            fifo_count := next_fifo_count;
        end if;
    end process;
end architecture;
