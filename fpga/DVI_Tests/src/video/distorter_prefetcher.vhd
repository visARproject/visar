library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.ram_port.all;
use work.video_bus.all;
use work.distorter_pkg.all;
use work.camera.all;

entity video_distorter_prefetcher is
    generic (
        LEFT_CAMERA_MEMORY_LOCATION : integer;
        RIGHT_CAMERA_MEMORY_LOCATION : integer;
        TABLE_MEMORY_LOCATION : integer);
    port (
        sync : in  video_sync;
        
        bram_ins  : out BRAMInArray;
        bram_outs : in  BRAMOutArray;
        
        ram1_in  : out ram_rd_port_in;
        ram1_out : in  ram_rd_port_out;
        ram2_in  : out ram_rd_port_in;
        ram2_out : in  ram_rd_port_out);
end entity;

architecture arc of video_distorter_prefetcher is
    signal h_cnt : HCountType;
    signal v_cnt : VCountType;
    
    signal reset : std_logic;
    
    signal table_decoder_en : std_logic;
    signal table_decoder_command : PrefetcherCommand;
    
    constant BURST_SIZE_WORDS : positive := 8;
    
    constant BUF_SIZE : positive := 16;
    type CoordinateBuf is array (0 to BUF_SIZE-1) of CameraCoordinate;
    signal pos_buf : CoordinateBuf;
begin
    u_counter : entity work.video_counter port map (
        sync => sync,
        h_cnt => h_cnt,
        v_cnt => v_cnt);
    
    process (v_cnt) is
    begin
        reset <= '0';
        if v_cnt = V_DISPLAY_END then
            reset <= '1';
        end if;
    end process;
    

    -- Commander
    
    U_TABLE_DECODER : entity work.video_distorter_prefetcher_table_decoder
        generic map (
            MEMORY_LOCATION => TABLE_MEMORY_LOCATION)
        port map (
            ram_in => ram2_in,
            ram_out => ram2_out,
            
            clock  => sync.pixel_clk,
            reset  => reset,
            en     => table_decoder_en,
            output => table_decoder_command);
    
    process (sync, h_cnt, v_cnt, reset, table_decoder_command) is
        variable pos_buf_write_pos, next_pos_buf_write_pos : integer range 0 to BUF_SIZE-1;
        variable delay_counter, next_delay_counter : DistorterDelay;
    begin
        ram1_in.cmd.clk <= sync.pixel_clk;
        
        ram1_in.cmd.en <= '0';
        ram1_in.cmd.instr <= (others => '-');
        ram1_in.cmd.byte_addr <= (others => '-');
        ram1_in.cmd.bl <= (others => '-');
        
        table_decoder_en <= '0';
        
        if reset = '1' then
            next_pos_buf_write_pos := 0;
            next_delay_counter := 2**9-1; -- initial delay to give time for first command to appear
        else
            if delay_counter > 0 then
                next_delay_counter := delay_counter - 1;
            else
                -- execute command in table_decoder_command
                next_delay_counter := table_decoder_command.delay;
                if pos_buf_write_pos /= BUF_SIZE-1 then
                    next_pos_buf_write_pos := pos_buf_write_pos + 1;
                else
                    next_pos_buf_write_pos := 0;
                end if;
                
                ram1_in.cmd.en <= '1';
                ram1_in.cmd.instr <= READ_PRECHARGE_COMMAND;
                if table_decoder_command.pos.x < CAMERA_WIDTH then
                    ram1_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                        LEFT_CAMERA_MEMORY_LOCATION + table_decoder_command.pos.y * CAMERA_STEP + table_decoder_command.pos.x
                    , ram1_in.cmd.byte_addr'length));
                else
                    ram1_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                        RIGHT_CAMERA_MEMORY_LOCATION + table_decoder_command.pos.y * CAMERA_STEP + (table_decoder_command.pos.x - CAMERA_WIDTH)
                    , ram1_in.cmd.byte_addr'length));
                end if;
                ram1_in.cmd.bl <= std_logic_vector(to_unsigned(BURST_SIZE_WORDS - 1, ram1_in.cmd.bl'length));
                
                table_decoder_en <= '1';
                
                if rising_edge(sync.pixel_clk) then
                    pos_buf(pos_buf_write_pos) <= table_decoder_command.pos;
                end if;
            end if;
        end if;
        
        if rising_edge(sync.pixel_clk) then
            pos_buf_write_pos := next_pos_buf_write_pos;
            delay_counter := next_delay_counter;
        end if;
    end process;
    
    -- RAM reader/BRAM writer
    
    process (sync, ram1_out, h_cnt, v_cnt, pos_buf, reset) is
        variable pos_buf_read_pos, next_pos_buf_read_pos : integer range 0 to BUF_SIZE-1;
        variable number_read, next_number_read : integer range 0 to BURST_SIZE_WORDS-1;
        variable command : CameraCoordinate;
        variable p : CameraCoordinate;
        variable next_bram_ins : BRAMInArray;
    begin
        ram1_in.rd.clk <= sync.pixel_clk;
        
        ram1_in.rd.en <= '0';
        
        for x in 0 to 7 loop
            for y in 0 to 7 loop
                bram_ins(x, y).clk <= sync.pixel_clk;
                bram_ins(x, y).dip <= (others => '-');
                bram_ins(x, y).we <= (others => '1');
                bram_ins(x, y).regce <= '-';
                bram_ins(x, y).rst <= '0';
                
                next_bram_ins(x, y).en := '0';
                next_bram_ins(x, y).di := (others => '-');
                next_bram_ins(x, y).addr := (others => '-');
            end loop;
        end loop;
        
        next_pos_buf_read_pos := pos_buf_read_pos;
        next_number_read := number_read;
        
        if reset = '1' then
            next_pos_buf_read_pos := 0;
            ram1_in.rd.en <= '1'; -- (try to) read extra to make sure FIFO is emptied
            next_number_read := 0;
        elsif ram1_out.rd.empty = '0' then
            for i in 0 to 3 loop
                p.y := command.x/4*4 + number_read * 4 + i;
                p.x := command.y;
                next_bram_ins(p.x mod 8, p.y mod 8).en := '1';
                next_bram_ins(p.x mod 8, p.y mod 8).di := "------------------------" & ram1_out.rd.data(8*i+7 downto 8*i);
                next_bram_ins(p.x mod 8, p.y mod 8).addr(13 downto 3) := std_logic_vector(to_unsigned(p.x/8 + 256*((p.y/8) mod 8), next_bram_ins(p.x mod 8, p.y mod 8).addr(13 downto 3)'length));
                next_bram_ins(p.x mod 8, p.y mod 8).addr(2 downto 0) := (others => '-');
            end loop;
            ram1_in.rd.en <= '1';
            if number_read /= BURST_SIZE_WORDS-1 then
                next_number_read := number_read + 1;
            else
                next_number_read := 0;
                if pos_buf_read_pos /= BUF_SIZE-1 then
                    next_pos_buf_read_pos := pos_buf_read_pos + 1;
                else
                    next_pos_buf_read_pos := 0;
                end if;
            end if;
        end if;
        
        if rising_edge(sync.pixel_clk) then
            command := pos_buf(next_pos_buf_read_pos);
            pos_buf_read_pos := next_pos_buf_read_pos;
            number_read := next_number_read;
            for x in 0 to 7 loop
                for y in 0 to 7 loop
                    bram_ins(x, y).en   <= next_bram_ins(x, y).en;
                    bram_ins(x, y).di   <= next_bram_ins(x, y).di;
                    bram_ins(x, y).addr <= next_bram_ins(x, y).addr;
                end loop;
            end loop;
        end if;
    end process;
end architecture;
