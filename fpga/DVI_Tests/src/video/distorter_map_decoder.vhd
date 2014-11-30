library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera_pkg.all;

entity video_distorter_map_decoder is
    port (
        data         : in  std_logic_vector(31 downto 0),
        data_advance : out std_logic;
        
        en    : in  std_logic;
        red   : out CameraCoordinate,
        green : out CameraCoordinate,
        blue  : out CameraCoordinate);
end entity;

architecture arc of video_distorter_map_decoder is
begin
    process (data) is
        variable green_tmp : CameraCoordinate;
    begin
        green_tmp.x <= to_integer(unsigned(data(11 downto  0)));
        green_tmp.y <= to_integer(unsigned(data(23 downto 12)));
        
        green <= green_tmp;
        
        --red.x <= green_tmp.x + to_integer(unsigned(data));
        --red.y <= green_tmp.x + to_integer(unsigned(data));
        red <= green_tmp; -- XXX
        
        blue <= green_tmp; -- XXX
        
        
        data_advance <= en;
    end process;
end architecture;
