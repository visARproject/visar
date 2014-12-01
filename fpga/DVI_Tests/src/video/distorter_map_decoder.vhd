library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera.all;
use work.ram_port.all;

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
    constant CHUNK_WORDS : integer := 5;
    
    type CameraInterpolationCoordinate is record
        x : integer range 0 to 2*CAMERA_WIDTH*N-1; -- stacked left-right because distorter buffer moves left-right
        y : integer range 0 to CAMERA_HEIGHT*N-1;
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
            MEMORY_LOCATION => memory_location,
            WORDS => CHUNK_WORDS)
        port map (
            ram_in => ram_in,
            ram_out => ram_out,
            clock => clock,
            reset => reset,
            en => ram_streamer_en,
            output => ram_streamer_output);
    
    process (clock, reset, en, ram_streamer_output) is
        variable first : CameraTripleCoordinate;
        variable last  : CameraTripleCoordinate;
        variable output_int, next_output_int : CameraTripleCoordinate;
        variable pos, next_pos : integer range 0 to SIZE-1;
    begin
        ram_streamer_en <= '0';
        
        output <= output_int;
        
        -- XXX need others here
        next_pos := pos;
        next_output_int := output_int;
        
        if reset = '1' then
            next_pos := SIZE-1;
        else
            if en = '1' then
                if pos /= SIZE-1 then
                    -- increment and output new result
                else
                    first.red  .x := to_integer(unsigned(ram_streamer_output( 12-1 downto   0)));
                    first.red  .y := to_integer(unsigned(ram_streamer_output( 23-1 downto  12)));
                    first.green.x := to_integer(unsigned(ram_streamer_output( 35-1 downto  23)));
                    first.green.y := to_integer(unsigned(ram_streamer_output( 46-1 downto  35)));
                    first.blue .x := to_integer(unsigned(ram_streamer_output( 58-1 downto  46)));
                    first.blue .y := to_integer(unsigned(ram_streamer_output( 69-1 downto  58)));
                    
                    last .red  .x := to_integer(unsigned(ram_streamer_output( 81-1 downto  69)));
                    last .red  .y := to_integer(unsigned(ram_streamer_output( 92-1 downto  81)));
                    last .green.x := to_integer(unsigned(ram_streamer_output(104-1 downto  92)));
                    last .green.y := to_integer(unsigned(ram_streamer_output(115-1 downto 104)));
                    last .blue .x := to_integer(unsigned(ram_streamer_output(127-1 downto 115)));
                    last .blue .y := to_integer(unsigned(ram_streamer_output(138-1 downto 127)));
                    
                    next_output_int := first;
                    
                    ram_streamer_en <= '1';
                end if;
            end if;
        end if;
        
        if rising_edge(clock) then
            -- XXX need others here
            output_int := next_output_int;
            pos := next_pos;
        end if;
    end process;
end architecture;
