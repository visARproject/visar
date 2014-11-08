library ieee;
use ieee.std_logic_1164.all;

package DVI_LIB is

	------------------------------------------------------
	-- Counter Values for Generating HSync and VSync
	constant HSYNC_BEGIN : integer := 1113;
	constant HSYNC_END 	 : integer := 1123;
	constant VSYNC_BEGIN : integer := 1921;
	constant VSYNC_END 	 : integer := 1927;
	constant H_DISPLAY_END	 : integer := 1080;
	constant V_DISPLAY_END  : integer := 1920;
	constant H_MAX 		 : positive := 1138;
	constant V_MAX 		 : positive := 1933;
	
	
end DVI_LIB;