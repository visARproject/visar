library IEEE;
use IEEE.STD_LOGIC_1164.all;

package video_bus is

    constant H_DISPLAY_END : integer := 1080;
    constant HSYNC_BEGIN   : integer := 1113;
    constant HSYNC_END     : integer := 1123;
    constant H_MAX         : integer := 1138;
    subtype HCountType is integer range 0 to H_MAX-1;
    
    constant V_DISPLAY_END : integer := 1920;
    constant VSYNC_BEGIN   : integer := 1921;
    constant VSYNC_END     : integer := 1927;
    constant V_MAX         : integer := 1933;
    subtype VCountType is integer range 0 to V_MAX-1;

    type video_sync is
    record
        pixel_clk : std_logic;
        frame_rst : std_logic; -- 1 for the last pixel of a frame
        valid     : std_logic; -- completely asynchronous to pixel_clk
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
