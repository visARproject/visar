library ieee;
library unisim;
use ieee.std_logic_1164.all;
use unisim.VCOMPONENTS.all;
use work.video_bus.all;

entity video_combiner is
    port(
        video_over  : in  video_data;
        video_under : in  video_data;
        video_out   : out video_data
    );
end entity video_combiner;

-- Architecture assumes that the video data signals are synchronized together.

architecture RTL of video_combiner is
    
begin
    process(video_over, video_under)
    begin
        -- If the overlay is black, then let the under_video through
        if(video_over.blue = x"00" and video_over.green = x"00" and video_over.red = x"00") then
            video_out <= video_under;
        else
            video_out <= video_over;
        end if;
              
              
        -- Later on add options for alpha layering.  For now, this is sufficient.
        
    end process;
end architecture RTL;
