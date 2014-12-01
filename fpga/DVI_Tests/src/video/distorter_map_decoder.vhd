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
        en     : in  std_logic;
        output : out CameraTripleCoordinate;
        valid  : out std_logic);
end entity;

architecture arc of video_distorter_map_decoder is
    constant N : integer := 16;
    constant SIZE : integer := 2*N+1;
begin
    process (ram_in, clock, en) is
        variable state, next_state : (STATE_START);
        variable current, next : std_logic_vector(32*5-1 downto 0);
        variable first : CameraTripleCoordinate;
        variable last  : CameraTripleCoordinate;
        variable fifo_count, next_fifo_count : integer range 0 to 100;
        variable pos : integer range 0 to SIZE-1;
        variable mem_pos, next_mem_pos : integer range 0 to 2**30-1;
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
            ram_in.rd.en <= '1';
            fifo_count := 0;
            next_mem_pos := memory_location;
        else
            if en = '1' then
                next_fifo_count := fifo_count - 1;
            end if;
            
            if next_fifo_count <= 32 then
                ram_in.cmd.en <= '1';
                ram_in.cmd.instr <= READ_PRECHARGE_COMMAND;
                ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                    (v_cnt * 2048 + h_cnt + 32) * 4
                , ram_in.cmd.byte_addr'length));
                ram_in.cmd.bl <= std_logic_vector(to_unsigned(32 - 1, ram_in.cmd.bl'length));
                
                next_fifo_count := next_fifo_count + 32;
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
