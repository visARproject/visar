library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;
use work.video_bus.all;

entity video_counter is
    port (
        sync : in video_sync;
        
        h_cnt : out HCountType;
        v_cnt : out VCountType);
end entity;

architecture arc of video_counter is
    signal h_cnt_int : HCountType;
    signal v_cnt_int : VCountType;
begin
    process (sync.pixel_clk) is
    begin
        if rising_edge(sync.pixel_clk) then
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
            
            if sync.frame_rst = '1' then
                h_cnt_int <= 0;
                v_cnt_int <= 0;
            end if;
        end if;
    end process;
    
    h_cnt <= h_cnt_int;
    v_cnt <= v_cnt_int;
end architecture;
