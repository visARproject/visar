library IEEE;
use IEEE.STD_LOGIC_1164.all;

package video_bus is

	constant H_DISPLAY_END	 : integer := 1080;
	constant HSYNC_BEGIN : integer := 1113;
	constant HSYNC_END 	 : integer := 1123;
	constant H_MAX 		 : positive := 1138;
	
	constant V_DISPLAY_END  : integer := 1920;
	constant VSYNC_BEGIN : integer := 1921;
	constant VSYNC_END 	 : integer := 1927;
	constant V_MAX 		 : positive := 1933;

    type video_sync is
    record
        pixel_clk : std_logic;
        frame_rst : std_logic; -- 1 for the last pixel of a frame
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
