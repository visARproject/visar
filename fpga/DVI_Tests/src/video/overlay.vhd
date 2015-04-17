library ieee;
library unisim;
use ieee.std_logic_1164.all;
use unisim.VCOMPONENTS.all;
use work.video_bus.all;

entity video_overlay is
    port(
        video_sync  : in  video_sync;
        video_over  : in  video_data;
        video_under : in  video_data;
        
        video_out   : out video_bus);
end entity video_overlay;

-- Architecture assumes that the video data signals are synchronized together.

architecture RTL of video_overlay is
    signal last_frame_rst : std_logic;
    signal transparent_color : video_data;
begin
    process (video_sync.pixel_clk) is
    begin
        video_out.sync.pixel_clk <= video_sync.pixel_clk;
        
        if rising_edge(video_sync.pixel_clk) then
            video_out.sync.frame_rst <= video_sync.frame_rst;
            video_out.sync.valid <= video_sync.valid;
            
            -- If the overlay is black, then let the under_video through
            if video_over.blue = transparent_color.blue and video_over.green = transparent_color.green and video_over.red = transparent_color.red then
                video_out.data <= video_under;
            else
                video_out.data <= video_over;
            end if;

            last_frame_rst <= video_sync.frame_rst;
            if last_frame_rst = '1' then
                transparent_color <= video_over;
            end if;

            -- Later on add options for alpha layering.  For now, this is sufficient.
        end if;
    end process;
end architecture RTL;
