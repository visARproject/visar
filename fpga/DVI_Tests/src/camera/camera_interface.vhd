library IEEE;
use IEEE.std_logic_1164.all;

package camera is
    type camera_out is record
        mclk : std_logic;
        rst  : std_logic;
        pwdn : std_logic;
    end record camera_out;

    type camera_inout is record
        sda  : std_logic;
        scl  : std_logic;
        pclk : std_logic; -- this and below are inout as a part of a workaround for IN_TERM bug AR# 40818
        lv   : std_logic;
        fv   : std_logic;
        data : std_logic_vector(7 downto 0);
    end record camera_inout;

end package;
