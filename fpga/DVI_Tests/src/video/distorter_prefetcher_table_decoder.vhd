library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera.all;
use work.ram_port.all;
use work.distorter_pkg.all;

entity video_distorter_prefetcher_table_decoder is
    generic (
        MEMORY_LOCATION : integer); -- needs to be 4-byte aligned
    port (
        ram_in  : out ram_rd_port_in;
        ram_out : in  ram_rd_port_out;
        
        clock  : in  std_logic;
        reset  : in  std_logic; -- must be asserted for "a while"
        en     : in  std_logic; -- acts like a normal FIFO - en is needed for first read; must not be asserted for "a while" after reset
        output : out PrefetcherCommand);
end entity;

architecture arc of video_distorter_prefetcher_table_decoder is
    constant CHUNK_WORDS : integer := 1;
    
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
        variable output_int, next_output_int : PrefetcherCommand;
    begin
        output <= output_int;
        
        ram_streamer_en <= '0';
        
        next_output_int := output_int;
        
        if reset = '1' then
        else
            if en = '1' then
                next_output_int.pos.x := to_integer(unsigned(ram_streamer_output(12-1 downto  0)));
                next_output_int.pos.y := to_integer(unsigned(ram_streamer_output(23-1 downto 12)));
                next_output_int.delay := to_integer(unsigned(ram_streamer_output(32-1 downto 23)));
                ram_streamer_en <= '1';
            end if;
        end if;
        
        if rising_edge(clock) then
            output_int := next_output_int;
        end if;
    end process;
end architecture;
