library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera_pkg.all;
use work.ram_port.all;

entity video_distorter_map_decoder is
    generic (
        MEMORY_LOCATION : integer); -- needs to be 4-byte aligned
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
    constant CHUNK_WORDS : integer := 5;
    
    type CameraInterpolationCoordinate is record
        x : integer range 0 to CAMERA_COLUMNS*N-1;
        y : integer range 0 to 2*CAMERA_ROWS*N-1; -- stacked up-down because distorter buffer moves up-down
    end record;
    
    type CameraTripleInterpolationCoordinate is record
        red   : CameraInterpolationCoordinate;
        green : CameraInterpolationCoordinate;
        blue  : CameraInterpolationCoordinate;
    end record;
    
    signal ram_streamer_en : std_logic;
    signal ram_streamer_output : std_logic_vector(CHUNK_WORDS*32-1 downto 0);
begin
    U_RAM_STREAMER : entity work.ram_streamer
        generic map (
            MEMORY_LOCATION => MEMORY_LOCATION,
            WORDS => CHUNK_WORDS)
        port map (
            ram_in => ram_in,
            ram_out => ram_out,
            clock => clock,
            reset => reset,
            en => ram_streamer_en,
            output => ram_streamer_output);
    
    process (clock, reset, en, ram_streamer_output) is
        variable first, next_first : CameraTripleCoordinate;
        variable last, next_last : CameraTripleCoordinate;
        variable tmp, next_tmp : CameraTripleInterpolationCoordinate;
        variable output_int, next_output_int : CameraTripleCoordinate;
        variable pos, next_pos : integer range 0 to SIZE-1;
    begin
        ram_streamer_en <= '0';
        
        output <= output_int;
        
        -- XXX need others here
        next_first := first;
        next_last := last;
        next_pos := pos;
        next_output_int := output_int;
        next_tmp := tmp;
        
        if reset = '1' then
            next_pos := SIZE-1;
        else
            if en = '1' then
                if pos /= SIZE-1 then
                    -- increment and output new result
                    next_pos := pos + 1;
                    next_tmp.red.x := tmp.red.x + (last.red.x - first.red.x);
                    next_tmp.red.y := tmp.red.y + (last.red.y - first.red.y);
                    next_tmp.green.x := tmp.green.x + (last.green.x - first.green.x);
                    next_tmp.green.y := tmp.green.y + (last.green.y - first.green.y);
                    next_tmp.blue.x := tmp.blue.x + (last.blue.x - first.blue.x);
                    next_tmp.blue.y := tmp.blue.y + (last.blue.y - first.blue.y);
                    
                    next_output_int.red.x := (next_tmp.red.x + N/2)/N;
                    next_output_int.red.y := (next_tmp.red.y + N/2)/N;
                    next_output_int.green.x := (next_tmp.green.x + N/2)/N;
                    next_output_int.green.y := (next_tmp.green.y + N/2)/N;
                    next_output_int.blue.x := (next_tmp.blue.x + N/2)/N;
                    next_output_int.blue.y := (next_tmp.blue.y + N/2)/N;
                else
                    next_first.red  .x := to_integer(unsigned(ram_streamer_output( 12-1 downto   0)));
                    next_first.red  .y := to_integer(unsigned(ram_streamer_output( 23-1 downto  12)));
                    next_first.green.x := to_integer(unsigned(ram_streamer_output( 35-1 downto  23)));
                    next_first.green.y := to_integer(unsigned(ram_streamer_output( 46-1 downto  35)));
                    next_first.blue .x := to_integer(unsigned(ram_streamer_output( 58-1 downto  46)));
                    next_first.blue .y := to_integer(unsigned(ram_streamer_output( 69-1 downto  58)));
                    
                    next_last .red  .x := to_integer(unsigned(ram_streamer_output( 81-1 downto  69)));
                    next_last .red  .y := to_integer(unsigned(ram_streamer_output( 92-1 downto  81)));
                    next_last .green.x := to_integer(unsigned(ram_streamer_output(104-1 downto  92)));
                    next_last .green.y := to_integer(unsigned(ram_streamer_output(115-1 downto 104)));
                    next_last .blue .x := to_integer(unsigned(ram_streamer_output(127-1 downto 115)));
                    next_last .blue .y := to_integer(unsigned(ram_streamer_output(138-1 downto 127)));
                    
                    next_tmp.red.x := next_first.red.x * N;
                    next_tmp.red.y := next_first.red.y * N;
                    next_tmp.green.x := next_first.green.x * N;
                    next_tmp.green.y := next_first.green.y * N;
                    next_tmp.blue.x := next_first.blue.x * N;
                    next_tmp.blue.y := next_first.blue.y * N;
                    
                    next_output_int := next_first;
                    
                    ram_streamer_en <= '1';
                    
                    next_pos := 0;
                end if;
            end if;
        end if;
        
        if rising_edge(clock) then
            -- XXX need others here
            output_int := next_output_int;
            first := next_first;
            last := next_last;
            pos := next_pos;
            tmp := next_tmp;
        end if;
    end process;
end architecture;
