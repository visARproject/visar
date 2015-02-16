library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package camera is
    type camera_out is record
        clock_p : std_logic;
        clock_n : std_logic;
    end record camera_out;

    type camera_in is record
        sync_p: std_logic;
        sync_n: std_logic;
        data0_p: std_logic;
        data0_n: std_logic;
        data1_p: std_logic;
        data1_n: std_logic;
        data2_p: std_logic;
        data2_n: std_logic;
        data3_p: std_logic;
        data3_n: std_logic;

        clock_p: std_logic;
        clock_n: std_logic;
    end record camera_in;
    
    type camera_output is record
        clock       : std_logic;
        data_valid  : std_logic; -- everything should be ignored if 0
        last_column : std_logic; -- 1 if (pixel1, pixel2) are last pair in line
        last_pixel  : std_logic; -- 1 if (pixel1, pixel2) are last pair in frame
        pixel1      : unsigned(9 downto 0); -- pixels will come in pairs when data_valid is 1
        pixel2      : unsigned(9 downto 0);
    end record;

    constant CAMERA_COLUMNS : integer := 1280;
    constant CAMERA_ROWS : integer := 1024;
    constant CAMERA_STEP : integer := 2048; -- should be CAMERA_COLUMNS rounded up to the next power of two
    
    type CameraCoordinate is record
        x : integer range 0 to 2*CAMERA_COLUMNS-1; -- stacked left-right because distorter buffer moves left-right
        y : integer range 0 to CAMERA_ROWS-1;
    end record;
    
    type CameraTripleCoordinate is record
        red   : CameraCoordinate;
        green : CameraCoordinate;
        blue  : CameraCoordinate;
    end record;
    
end package;
