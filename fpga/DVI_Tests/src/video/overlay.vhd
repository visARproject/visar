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

begin
    process(video_over, video_under)
    begin
        if rising_edge(video_sync.pixel_clk) then
            video_out.sync.frame_rst <= video_sync.frame_rst;
            video_out.sync.valid <= video_sync.valid;
            
            -- If the overlay is black, then let the under_video through
            if(video_over.blue = x"00" and video_over.green = x"00" and video_over.red = x"00") then
                video_out.data <= video_under;
            else
                video_out.data <= video_over;
            end if;


            -- Later on add options for alpha layering.  For now, this is sufficient.
        end if;
    end process;
end architecture RTL;
