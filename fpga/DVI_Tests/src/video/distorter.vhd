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
    generic (
        LEFT_CAMERA_MEMORY_LOCATION : integer;
        RIGHT_CAMERA_MEMORY_LOCATION : integer;
        PREFETCHER_TABLE_MEMORY_LOCATION : integer;
        MAP_MEMORY_LOCATION : integer);
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
    signal bram_porta_ins, bram_portb_ins_4 : BRAMInArray;
    signal bram_porta_outs, bram_portb_outs_2 : BRAMOutArray;
    
    
    signal h_cnt_1future : HCountType;
    signal v_cnt_1future : VCountType;
    
    signal h_cnt : HCountType;
    signal v_cnt : VCountType;
    
    signal map_decoder_reset, map_decoder_en: std_logic;
    signal current_lookup_5 : CameraTripleCoordinate;
begin
    GEN_BRAM1: for x in 0 to 7 generate
        GEN_BRAM2: for y in 0 to 7 generate
            BRAM : RAMB16BWER
                generic map (
                    DATA_WIDTH_A => 9,
                    DATA_WIDTH_B => 9,
                    DOA_REG      => 1,
                    DOB_REG      => 1,
                    SIM_DEVICE   => "SPARTAN6")
                port map (
                    ADDRA  => bram_porta_ins(x, y).addr,
                    ADDRB  => bram_portb_ins_4(x, y).addr,
                    DIA    => bram_porta_ins(x, y).di,
                    DIB    => bram_portb_ins_4(x, y).di,
                    DIPA   => bram_porta_ins(x, y).dip,
                    DIPB   => bram_portb_ins_4(x, y).dip,
                    WEA    => bram_porta_ins(x, y).we,
                    WEB    => bram_portb_ins_4(x, y).we,
                    CLKA   => bram_porta_ins(x, y).clk,
                    CLKB   => bram_portb_ins_4(x, y).clk,
                    ENA    => bram_porta_ins(x, y).en,
                    ENB    => bram_portb_ins_4(x, y).en,
                    REGCEA => bram_porta_ins(x, y).regce,
                    REGCEB => bram_portb_ins_4(x, y).regce,
                    RSTA   => bram_porta_ins(x, y).rst,
                    RSTB   => bram_portb_ins_4(x, y).rst,

                    DOA  => bram_porta_outs(x, y).do,
                    DOB  => bram_portb_outs_2(x, y).do,
                    DOPA => bram_porta_outs(x, y).dop,
                    DOPB => bram_portb_outs_2(x, y).dop);
        end generate;
    end generate;
    
    U_PREFETCHER : entity work.video_distorter_prefetcher
        generic map (
            LEFT_CAMERA_MEMORY_LOCATION => LEFT_CAMERA_MEMORY_LOCATION,
            RIGHT_CAMERA_MEMORY_LOCATION => RIGHT_CAMERA_MEMORY_LOCATION,
            TABLE_MEMORY_LOCATION => PREFETCHER_TABLE_MEMORY_LOCATION)
        port map (
            sync => sync,
            bram_ins => bram_porta_ins,
            bram_outs => bram_porta_outs,
            ram1_in => ram1_in,
            ram1_out => ram1_out,
            ram2_in => ram2_in,
            ram2_out => ram2_out);
    
    
    -- Actual distorter
    
    u_counter2 : entity work.video_counter
        generic map(
            DELAY => -1)
        port map (
            sync => sync,
            h_cnt => h_cnt_1future,
            v_cnt => v_cnt_1future);
    
    u_counter : entity work.video_counter port map (
        sync => sync,
        h_cnt => h_cnt,
        v_cnt => v_cnt);
    
    process (h_cnt_1future, v_cnt_1future, v_cnt) is
    begin
        map_decoder_reset <= '0';
        map_decoder_en <= '0';
        if v_cnt = V_DISPLAY_END then
            map_decoder_reset <= '1';
        end if;
        if v_cnt_1future < V_DISPLAY_END and h_cnt_1future < 1089 then
            map_decoder_en <= '1';
        end if;
    end process;
    
    U_MAP_DECODER : entity work.video_distorter_map_decoder
        generic map (
            MEMORY_LOCATION => MAP_MEMORY_LOCATION)
        port map (
            ram_in => ram3_in,
            ram_out => ram3_out,
            
            clock  => sync.pixel_clk,
            reset  => map_decoder_reset,
            en     => map_decoder_en,
            output => current_lookup_5);
    
    
    process (sync.pixel_clk, bram_portb_outs_2, current_lookup_5) is
        variable center_5, center_4, center_3, center_2, center_1 : CameraCoordinate;
        variable dx_5, dy_5 : integer range -4 to 3;
        variable px_5 : CameraCoordinate;
        type SampleArray is array (7 downto 0, 7 downto 0) of integer range 0 to 255;
        variable samples_1 : SampleArray;
    begin
        center_5 := current_lookup_5.green;
        
        for memx in 0 to 7 loop
            for memy in 0 to 7 loop
                dx_5 := (memx - center_5.x + 4) mod 8 - 4; -- solving for dx in (center_5.x + dx) mod 8 = x with dx constrained to [-4, 3]
                dy_5 := (memy - center_5.y + 4) mod 8 - 4;
                px_5.x := center_5.x + dx_5;
                px_5.y := center_5.y + dy_5;
                
                bram_portb_ins_4(memx, memy).clk <= sync.pixel_clk;
                if rising_edge(sync.pixel_clk) then
                    bram_portb_ins_4(memx, memy).addr(13 downto 3) <= std_logic_vector(to_unsigned(
                        256*((px_5.x/8) mod 8) + px_5.y/8
                    , bram_portb_ins_4(memx, memy).addr(13 downto 3)'length));
                    bram_portb_ins_4(memx, memy).addr(2 downto 0) <= (others => '-');
                    bram_portb_ins_4(memx, memy).di <= (others => '-');
                    bram_portb_ins_4(memx, memy).dip <= (others => '-');
                    bram_portb_ins_4(memx, memy).we <= (others => '0');
                    bram_portb_ins_4(memx, memy).en <= '1';
                    bram_portb_ins_4(memx, memy).regce <= '1';
                    bram_portb_ins_4(memx, memy).rst <= '0';
                    
                    samples_1(memx, memy) := to_integer(unsigned(bram_portb_outs_2(memx, memy).do(7 downto 0)));
                end if;
            end loop;
        end loop;
        
        if rising_edge(sync.pixel_clk) then
            if center_1.x = 0 and center_1.y = 0 then
                data_out.red <= x"20";
                data_out.green <= x"10";
                data_out.blue <= x"10";
            else
                data_out.red   <= std_logic_vector(to_unsigned(samples_1((center_1.x mod 8)/2*2+1, (center_1.y mod 8)/2*2+0), data_out.red'length));
                data_out.green <= std_logic_vector(to_unsigned(samples_1((center_1.x mod 8)/2*2+0, (center_1.y mod 8)/2*2+0), data_out.green'length)); -- 0 0 or 1 1
                data_out.blue  <= std_logic_vector(to_unsigned(samples_1((center_1.x mod 8)/2*2+0, (center_1.y mod 8)/2*2+1), data_out.blue'length));
            end if;
            center_1 := center_2;
            center_2 := center_3;
            center_3 := center_4;
            center_4 := center_5;
        end if;
    end process;
end architecture;
