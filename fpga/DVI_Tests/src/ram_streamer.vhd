library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera_pkg.all;

entity video_distorter_map_decoder is
    generic (
        MEMORY_LOCATION : integer, -- needs to be 4-byte aligned
        WORDS           : natural);
    port (
        ram_in  : out ram_rd_port_in;
        ram_out : in  ram_rd_port_out;
        
        clock  : in  std_logic;
        reset  : in  std_logic; -- must be asserted for "a while"
        en     : in  std_logic; -- acts like a normal FIFO - en is needed for first read; must not be asserted for "a while" after reset
        output : out std_logic_vector(32*WORDS-1 downto 0));
end entity;

architecture arc of video_distorter_map_decoder is
    constant READ_BURST_LENGTH_WORDS : integer := 32;
begin
    process (ram_in, clock, en) is
        variable current, next_current : std_logic_vector(32*WORDS-1 downto 0);
        variable current_loaded, next_current_loaded : std_logic;
        variable current_load_pos, next_current_load_pos : integer range 0 to WORDS-1;
        variable fifo_count, next_fifo_count : integer range 0 to 2*RAM_FIFO_LENGTH;
        variable mem_pos, next_mem_pos : integer range memory_location to memory_location+2**27-1;
    begin
        ram_in.cmd.clk <= clock;
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        
        ram_in.rd.clk <= clock;
        ram_in.rd.en <= '0';
        
        output <= (others => '-');
        
        -- XXX need others here
        next_fifo_count := fifo_count;
        
        if reset = '1' then
            next_current_loaded := '0';
            next_next_loaded := '0';
            next_fifo_count := 0;
            next_pos := SIZE-1;
            next_mem_pos := memory_location;
            
            ram_in.rd.en <= '1';
        else
            output <= current;
            if en = '1' then
                next_current_loaded := '0';
            end if;
            
            -- keep current loaded
            if next_current_loaded = '0' and ram_in.rd.empty = '0' then
                next_current(current_load_pos*32+31 downto current_load_pos*32) := ram_in.rd.data;
                ram_in.rd.en <= '1';
                next_fifo_count := fifo_count - 1;
                if current_load_pos /= 4 then
                    next_current_load_pos := current_load_pos + 1;
                else
                    next_current_loaded := '1';
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
        
        if rising_edge(clock) then
            -- XXX need others here
            fifo_count := next_fifo_count;
        end if;
    end process;
end architecture;
