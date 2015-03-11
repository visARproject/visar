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
        en     : in  std_logic; -- acts like a first-word-fallthrough FIFO; must not be asserted for "a while" after reset
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
    begin
        ram_streamer_en <= en;
        
        output.pos.x <= to_integer(unsigned(ram_streamer_output(11-1 downto  0)));
        output.pos.y <= to_integer(unsigned(ram_streamer_output(22-1 downto 11)));
        output.delay <= to_integer(unsigned(ram_streamer_output(32-1 downto 22)));
    end process;
end architecture;
