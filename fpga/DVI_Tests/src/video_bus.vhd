library IEEE;
use IEEE.STD_LOGIC_1164.all;

package video_bus is

    type video_sync is
    record
        pixel_clk : std_logic;
        frame_rst : std_logic;
        valid     : std_logic;
    end record;

    type video_data is
    record
        red   : std_logic_vector(7 downto 0);
        green : std_logic_vector(7 downto 0);
        blue  : std_logic_vector(7 downto 0);
    end record;

    type video_bus is
    record
        sync : video_sync;
        data : video_data;
    end record;

end video_bus;

package body video_bus is
 
end video_bus;
