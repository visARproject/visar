library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.ram_port.all;
use work.video_bus.all;
use work.distorter_pkg.all;
use work.camera.all;

entity video_distorter is
    port (
        sync     : in  video_sync;
        data_out : out video_data;
        
        ram1_in  : out ram_rd_port_in;
        ram1_out : in  ram_rd_port_out;
        ram2_in  : out ram_rd_port_in;
        ram2_out : in  ram_rd_port_out;
        ram3_in  : out ram_rd_port_in;
        ram3_out : in  ram_rd_port_out);
end entity;

architecture arc of video_distorter is
    signal h_cnt : HCountType;
    signal v_cnt : VCountType;
    
    type InArray is array (7 downto 0, 7 downto 0) of bram_port_in;
    signal bram_porta_ins, bram_portb_ins : InArray;
    type OutArray is array (7 downto 0, 7 downto 0) of bram_port_out;
    signal bram_porta_outs, bram_portb_outs : OutArray;
begin
    u_counter : entity work.video_counter port map (
        sync => sync,
        h_cnt => h_cnt,
        v_cnt => v_cnt);
    
    GEN_BRAM1: for x in 0 to 7 generate
        GEN_BRAM2: for y in 0 to 7 generate
            BRAM : RAMB16BWER
                generic map (
                    DATA_WIDTH_A => 9,
                    DATA_WIDTH_B => 9,
                    DOA_REG      => 1,
                    DOB_REG      => 1)
                port map (
                    ADDRA  => bram_porta_ins(x, y).addr,
                    ADDRB  => bram_portb_ins(x, y).addr,
                    DIA    => bram_porta_ins(x, y).di,
                    DIB    => bram_portb_ins(x, y).di,
                    DIPA   => bram_porta_ins(x, y).dip,
                    DIPB   => bram_portb_ins(x, y).dip,
                    WEA    => bram_porta_ins(x, y).we,
                    WEB    => bram_portb_ins(x, y).we,
                    CLKA   => bram_porta_ins(x, y).clk,
                    CLKB   => bram_portb_ins(x, y).clk,
                    ENA    => bram_porta_ins(x, y).en,
                    ENB    => bram_portb_ins(x, y).en,
                    REGCEA => bram_porta_ins(x, y).regce,
                    REGCEB => bram_portb_ins(x, y).regce,
                    RSTA   => bram_porta_ins(x, y).rst,
                    RSTB   => bram_portb_ins(x, y).rst,

                    DOA  => bram_porta_outs(x, y).do,
                    DOB  => bram_portb_outs(x, y).do,
                    DOPA => bram_porta_outs(x, y).dop,
                    DOPB => bram_portb_outs(x, y).dop);
        end generate;
    end generate;
    
    -- Prefetcher
    
    process (sync, h_cnt, v_cnt) is
    begin
        for x in 0 to 7 loop
            for y in 0 to 7 loop
                bram_porta_ins(x, y).addr <= (others => '-');
                bram_porta_ins(x, y).di <= (others => '-');
                bram_porta_ins(x, y).dip <= (others => '-');
                bram_porta_ins(x, y).we <= (others => '-');
                bram_porta_ins(x, y).clk <= sync.pixel_clk;
                bram_porta_ins(x, y).en <= '0';
                bram_porta_ins(x, y).regce <= '0';
                bram_porta_ins(x, y).rst <= '0';
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
    
    -- Actual distorter
    
    process (sync.pixel_clk, bram_portb_outs) is
        variable centerx, centery : integer;
        variable dx, dy : integer range -4 to 3;
        variable pxx : integer range 0 to CAMERA_WIDTH-1;
        variable pxy : integer range 0 to CAMERA_HEIGHT-1;
        type SampleArray is array (7 downto 0, 7 downto 0) of integer range 0 to 511;
        variable samples : SampleArray;
    begin
        centerx := 640;
        centery := 480;
        
        for memx in 0 to 7 loop
            for memy in 0 to 7 loop
                dx := (memx - centerx + 4) mod 8 - 4; -- solving for dx in (centerx + dx) mod 8 = x with dx constrained to [-4, 3]
                dy := (memy - centery + 4) mod 8 - 4;
                pxx := centerx + dx;
                pxy := centerx + dy;
                bram_portb_ins(memx, memy).addr(13 downto 3) <= std_logic_vector(to_unsigned(
                    pxx/8 + 160*((pxy/8)*171 mod 2048) -- equivalent to pxx/8 + 160*(pxy/8 mod 12)
                , bram_portb_ins(memx, memy).addr(13 downto 3)'length));
                bram_portb_ins(memx, memy).addr(2 downto 0) <= (others => '-');
                bram_portb_ins(memx, memy).di <= (others => '-');
                bram_portb_ins(memx, memy).dip <= (others => '-');
                bram_portb_ins(memx, memy).we <= (others => '0');
                bram_portb_ins(memx, memy).clk <= sync.pixel_clk;
                bram_portb_ins(memx, memy).en <= '1';
                bram_portb_ins(memx, memy).regce <= '1';
                bram_portb_ins(memx, memy).rst <= '0';
                
                samples(memx, memy) := to_integer(unsigned(
                    bram_portb_outs(memx, memy).do(7 downto 0) &
                    bram_portb_outs(memx, memy).dop(0 downto 0)));
            end loop;
        end loop;
        
        data_out.red   <= std_logic_vector(to_unsigned(samples(0, 0), data_out.red'length));
        data_out.green <= std_logic_vector(to_unsigned(samples(0, 1), data_out.green'length));
        data_out.blue  <= std_logic_vector(to_unsigned(samples(1, 1), data_out.blue'length));
    end process;
end architecture;
