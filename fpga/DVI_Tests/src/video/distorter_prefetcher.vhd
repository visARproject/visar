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
    
    signal table_decoder_reset, table_decoder_en : std_logic;
    signal command : PrefetcherCommand;
    
    constant BUF_SIZE : positive := 16;
    type CoordinateBuf is array (0 to BUF_SIZE-1) of CameraCoordinate;
    signal pos_buf : CoordinateBuf;
    signal pos_buf_read_pos, pos_buf_write_pos : integer range 0 to BUF_SIZE-1;
begin
    u_counter : entity work.video_counter port map (
        sync => sync,
        h_cnt => h_cnt,
        v_cnt => v_cnt);
    
    U_TABLE_DECODER : entity work.video_distorter_prefetcher_table_decoder
        generic map (
            MEMORY_LOCATION => TABLE_MEMORY_LOCATION)
        port map (
            ram_in => ram2_in,
            ram_out => ram2_out,
            
            clock  => sync.pixel_clk,
            reset  => table_decoder_reset,
            en     => table_decoder_en,
            output => command);
    
    process (sync, h_cnt, v_cnt) is
    begin
        for x in 0 to 7 loop
            for y in 0 to 7 loop
                bram_ins(x, y).addr <= (others => '-');
                bram_ins(x, y).di <= (others => '-');
                bram_ins(x, y).dip <= (others => '-');
                bram_ins(x, y).we <= (others => '-');
                bram_ins(x, y).clk <= sync.pixel_clk;
                bram_ins(x, y).en <= '0';
                bram_ins(x, y).regce <= '0';
                bram_ins(x, y).rst <= '0';
            end loop;
        end loop;
        
        ram1_in.cmd.clk <= sync.pixel_clk;
        
        ram1_in.cmd.en <= '0';
        ram1_in.cmd.instr <= (others => '-');
        ram1_in.cmd.byte_addr <= (others => '-');
        ram1_in.cmd.bl <= (others => '-');
        
        if h_cnt mod 32 = 0 and h_cnt < H_DISPLAY_END and v_cnt < V_DISPLAY_END then
            ram1_in.cmd.en <= '1';
            ram1_in.cmd.instr <= READ_PRECHARGE_COMMAND;
            ram1_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                (v_cnt * 2048 + h_cnt + 32) * 4
            , ram1_in.cmd.byte_addr'length));
            ram1_in.cmd.bl <= std_logic_vector(to_unsigned(32 - 1, ram1_in.cmd.bl'length));
        end if;
    end process;
    
    process (sync, ram1_out, h_cnt, v_cnt) is
    begin
        --ram1_out.rd.data( 7 downto  0);
        
        ram1_in.rd.clk <= sync.pixel_clk;
        
        ram1_in.rd.en <= '0';
        if h_cnt >= 32 and v_cnt < V_DISPLAY_END + 1 then -- (try to) read extra to make sure FIFO is emptied
            ram1_in.rd.en <= '1';
        end if;
    end process;
end architecture;
