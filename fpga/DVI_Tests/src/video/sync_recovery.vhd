library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;
use work.video_bus.all;

entity video_sync_recovery is
    port (
        valid       : in std_logic;
        pixel_clock : in std_logic;
        hsync       : in std_logic;
        vsync       : in std_logic;
        
        sync_out : out video_sync);
end entity;

architecture arc of video_sync_recovery is
    signal hsync_prev, vsync_prev : std_logic;
    
    signal h_cnt_int : HCountType;
    signal v_cnt_int : VCountType;
begin
    process (pixel_clock) is
    begin
        if rising_edge(pixel_clock) then
            if h_cnt_int /= H_MAX - 1 then
                h_cnt_int <= h_cnt_int + 1;
            elsif h_cnt_int = H_MAX - 1 then
                h_cnt_int <= 0;
                if v_cnt_int /= V_MAX - 1 then
                    v_cnt_int <= v_cnt_int + 1;
                else
                    v_cnt_int <= 0;
                end if;
            end if;
            
            -- Synchronization
            hsync_prev <= hsync;    
            vsync_prev <= vsync;
            
            if hsync_prev = '1' and hsync = '0' then
                h_cnt_int <= HSYNC_END + 1;
            end if;
            
            if vsync_prev = '0' and vsync = '1' then
                v_cnt_int <= VSYNC_END + 1;
            end if;    
        end if;
    end process;
    
    sync_out.valid <= valid;
    sync_out.pixel_clk <= pixel_clock;
    
    process (h_cnt_int, v_cnt_int) is
    begin
        sync_out.frame_rst <= '0';
        if h_cnt_int = H_MAX - 1 and v_cnt_int = V_MAX - 1 then
            sync_out.frame_rst <= '1';
        end if;
    end process;
end architecture;
