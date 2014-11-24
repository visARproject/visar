library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.video_bus.all;

entity video_sync_gen is
    port (
        sync         : in video_sync;
        
        data_en      : out std_logic;
        h_sync       : out std_logic;
        v_sync       : out std_logic);
end entity video_sync_gen;

architecture Behavioral of video_sync_gen is
    signal h_cnt : HCountType;
    signal v_cnt : VCountType;
begin
    u_counter : entity work.video_counter port map (
        sync => sync,
        h_cnt => h_cnt,
        v_cnt => v_cnt);
    
    process (h_cnt, v_cnt) is
    begin
        if h_cnt < H_DISPLAY_END and v_cnt < V_DISPLAY_END then
            data_en <= '1';
        else
            data_en <= '0';        
        end if;
        
        -- +hsync -vsync
        
        if h_cnt >= HSYNC_BEGIN and h_cnt < HSYNC_END then
            h_sync <= '1';
        else
            h_sync <= '0';
        end if;
        
        if v_cnt >= VSYNC_BEGIN and v_cnt < VSYNC_END then
            v_sync <= '0';
        else
            v_sync <= '1';
        end if;
    end process;
end Behavioral;
