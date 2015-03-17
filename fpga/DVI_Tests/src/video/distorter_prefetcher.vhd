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
    
    constant BURST_SIZE_WORDS : positive := 16; -- has to be a multiple of 4
    
    constant BUF_SIZE : positive := 32;
    type CoordinateBuf is array (0 to BUF_SIZE-1) of CameraCoordinate;
    signal pos_buf : CoordinateBuf;
    
    signal fifo_write_full  : std_logic;
    signal fifo_read_enable : std_logic;
    signal fifo_read_data   : std_logic_vector(39 downto 0);
    signal fifo_read_empty  : std_logic;
begin
    u_counter : entity work.video_counter
        generic map (
            DELAY => -5000)
        port map (
            sync => sync,
            h_cnt => h_cnt,
            v_cnt => v_cnt);
    
    process (v_cnt) is
    begin
        reset <= '0';
        if v_cnt = V_MAX-1 then
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
    
    process (sync, h_cnt, v_cnt, reset, table_decoder_command, ram1_out) is
        variable pos_buf_write_pos, next_pos_buf_write_pos : integer range 0 to BUF_SIZE-1;
        variable delay_counter, next_delay_counter : DistorterDelay;
        variable command, next_command: PrefetcherCommand;
        variable write_pos : boolean;
    begin
        ram1_in.cmd.clk <= sync.pixel_clk;
        
        ram1_in.cmd.en <= '0';
        ram1_in.cmd.instr <= (others => '-');
        ram1_in.cmd.byte_addr <= (others => '-');
        ram1_in.cmd.bl <= (others => '-');
        
        table_decoder_en <= '0';
        
        next_pos_buf_write_pos := pos_buf_write_pos;
        next_delay_counter := delay_counter;
        next_command := command;
        write_pos := false;
        
        if reset = '1' then
            next_pos_buf_write_pos := 0;
            next_delay_counter := 0;
            next_command := (
                delay => 2**9-1, -- initial delay to give time for first command to appear
                pos => (
                    x => 0,
                    y => 0));
        else
            if delay_counter /= command.delay then
                next_delay_counter := delay_counter + 1;
            else
                -- execute command in command
                next_delay_counter := 0;
                
                if ram1_out.cmd.full = '0' then
                    if pos_buf_write_pos /= BUF_SIZE-1 then
                        next_pos_buf_write_pos := pos_buf_write_pos + 1;
                    else
                        next_pos_buf_write_pos := 0;
                    end if;
                    
                    ram1_in.cmd.en <= '1';
                    ram1_in.cmd.instr <= READ_PRECHARGE_COMMAND;
                    if command.pos.y < CAMERA_ROWS then
                        ram1_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                            LEFT_CAMERA_MEMORY_LOCATION + command.pos.y * CAMERA_STEP + command.pos.x*4
                        , ram1_in.cmd.byte_addr'length));
                    else
                        ram1_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                            RIGHT_CAMERA_MEMORY_LOCATION + (command.pos.y - CAMERA_ROWS) * CAMERA_STEP + command.pos.x*4
                        , ram1_in.cmd.byte_addr'length));
                    end if;
                    ram1_in.cmd.bl <= std_logic_vector(to_unsigned(BURST_SIZE_WORDS - 1, ram1_in.cmd.bl'length));
                    
                    write_pos := true;
                end if;
                
                table_decoder_en <= '1';
                next_command := table_decoder_command;
            end if;
        end if;
        
        if rising_edge(sync.pixel_clk) then
            pos_buf_write_pos := next_pos_buf_write_pos;
            delay_counter := next_delay_counter;
            command := next_command;
            if write_pos then
                pos_buf(pos_buf_write_pos) <= command.pos;
            end if;
        end if;
    end process;

    -- RAM reader/BRAM writer
    
    U_PIXEL_FIFO : entity work.util_fifo_fallthrough
        generic map (
            WIDTH       => 120,
            LOG_2_DEPTH => 4,
            WRITE_WIDTH => 30,
            READ_WIDTH  => 40)
        port map (
            write_clock  => sync.pixel_clk,
            write_reset  => reset,
            write_enable => not ram1_out.rd.empty,
            write_full   => fifo_write_full,
            write_data   => ram1_out.rd.data(9 downto 0) & ram1_out.rd.data(19 downto 10) & ram1_out.rd.data(29 downto 20),
            
            read_clock  => sync.pixel_clk,
            read_reset  => reset,
            read_enable => fifo_read_enable,
            read_data   => fifo_read_data,
            read_empty  => fifo_read_empty);
    ram1_in.rd.en <= not fifo_write_full and not ram1_out.rd.empty;
    
    
    process (sync, fifo_read_data, fifo_read_empty, h_cnt, v_cnt, pos_buf, reset) is
        variable pos_buf_read_pos, next_pos_buf_read_pos : integer range 0 to BUF_SIZE-1;
        variable number_read, next_number_read : integer range 0 to BURST_SIZE_WORDS*3/4-1;
        variable command : CameraCoordinate;
        variable p : CameraCoordinate;
        variable next_bram_ins, next_next_bram_ins : BRAMInArray;
        variable encoded : std_logic_vector(8 downto 0);
    begin
        ram1_in.rd.clk <= sync.pixel_clk;
        
        fifo_read_enable <= '0';
        
        for x in 0 to 7 loop
            for y in 0 to 7 loop
                bram_ins(x, y).clk <= sync.pixel_clk;
                bram_ins(x, y).we <= (others => '1');
                bram_ins(x, y).regce <= '-';
                bram_ins(x, y).rst <= '0';
                
                next_next_bram_ins(x, y).en := '0';
                next_next_bram_ins(x, y).di := (others => '-');
                next_next_bram_ins(x, y).dip := (others => '-');
                next_next_bram_ins(x, y).addr := (others => '-');
            end loop;
        end loop;
        
        next_pos_buf_read_pos := pos_buf_read_pos;
        next_number_read := number_read;
        
        if reset = '1' then
            next_pos_buf_read_pos := 0;
            next_number_read := 0;
        elsif fifo_read_empty = '0' then
            for i in 0 to 3 loop
                p.x := command.x/8*8 + command.x/8*8*2 + number_read * 4 + i;
                p.y := command.y;
                encoded := encode_10to9(unsigned(fifo_read_data(10*(3-i)+9 downto 10*(3-i))));
                next_next_bram_ins(p.x mod 8, p.y mod 8).en := '1';
                next_next_bram_ins(p.x mod 8, p.y mod 8).di := "------------------------" & encoded(7 downto 0);
                next_next_bram_ins(p.x mod 8, p.y mod 8).addr(13 downto 3) := std_logic_vector(to_unsigned(
                    256*((p.y/8) mod 8) + p.x/8
                , next_next_bram_ins(p.x mod 8, p.y mod 8).addr(13 downto 3)'length));
                next_next_bram_ins(p.x mod 8, p.y mod 8).dip := "---" & encoded(8);
                next_next_bram_ins(p.x mod 8, p.y mod 8).addr(2 downto 0) := (others => '-');
            end loop;
            fifo_read_enable <= '1';
            if number_read /= BURST_SIZE_WORDS*3/4-1 then
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
                    bram_ins(x, y).dip  <= next_bram_ins(x, y).dip;
                    bram_ins(x, y).addr <= next_bram_ins(x, y).addr;
                    
                    next_bram_ins(x, y).en   := next_next_bram_ins(x, y).en;
                    next_bram_ins(x, y).di   := next_next_bram_ins(x, y).di;
                    next_bram_ins(x, y).dip  := next_next_bram_ins(x, y).dip;
                    next_bram_ins(x, y).addr := next_next_bram_ins(x, y).addr;
                end loop;
            end loop;
        end if;
    end process;
end architecture;
