library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.camera_pkg.all;
use work.ram_port.all;

entity camera is
    generic (
        SYNC_INVERTED   : boolean;
        DATA3_INVERTED  : boolean;
        DATA2_INVERTED  : boolean;
        DATA1_INVERTED  : boolean;
        DATA0_INVERTED  : boolean;
        MEMORY_LOCATION : integer); -- needs to be 4-byte aligned
    port (
        clock_camera_unbuf  : in std_logic;
        clock_camera_over_2 : in std_logic;
        clock_camera_over_5 : in std_logic;
        clock_locked        : in std_logic;
        reset               : in std_logic;
        
        camera_out : out camera_out;
        camera_in  : in  camera_in;
        
        ram_in  : out ram_wr_port_in;
        ram_out : in  ram_wr_port_out);
end camera;

architecture arc of camera is
    signal camera_output : camera_output;
begin
    U_CAMERA_WRAPPER : entity work.camera_wrapper
        generic map (
            SYNC_INVERTED  => SYNC_INVERTED,
            DATA3_INVERTED => DATA3_INVERTED,
            DATA2_INVERTED => DATA2_INVERTED,
            DATA1_INVERTED => DATA1_INVERTED,
            DATA0_INVERTED => DATA0_INVERTED)
        port map (
            clock_camera_unbuf  => clock_camera_unbuf,
            clock_camera_over_2 => clock_camera_over_2,
            clock_camera_over_5 => clock_camera_over_5,
            clock_locked        => clock_locked,
            reset               => reset,
            
            camera_out => camera_out,
            camera_in  => camera_in,
            
            output => camera_output);
    
    U_CAMERA_WRITER : entity work.camera_writer
        generic map (
            BUFFER_ADDRESS => MEMORY_LOCATION)
        port map (
            camera_output => camera_output,
            
            ram_in  => ram_in,
            ram_out => ram_out);
end architecture;
