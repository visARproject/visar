library IEEE;
use IEEE.std_logic_1164.all;

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
        data        : std_logic_vector(7 downto 0);
        data_valid  : std_logic;
        frame_valid : std_logic;
    end record;

    constant CAMERA_WIDTH : integer := 1600;
    constant CAMERA_HEIGHT : integer := 1200;
    constant CAMERA_STEP : integer := 2048; -- should be CAMERA_WIDTH rounded up to the next power of two
    
    type CameraCoordinate is record
        x : integer range 0 to 2*CAMERA_WIDTH-1; -- stacked left-right because distorter buffer moves left-right
        y : integer range 0 to CAMERA_HEIGHT-1;
    end record;
    
    type CameraTripleCoordinate is record
        red   : CameraCoordinate;
        green : CameraCoordinate;
        blue  : CameraCoordinate;
    end record;
    
end package;
