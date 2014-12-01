library ieee;
use ieee.std_logic_1164.all;

use work.camera.all;

package distorter_pkg is

    type bram_port_in is
    record
        addr  : std_logic_vector(13 downto 0);
        di    : std_logic_vector(31 downto 0);
        dip   : std_logic_vector(3 downto 0);
        we    : std_logic_vector(3 downto 0);
        clk   : std_logic;
        en    : std_logic;
        regce : std_logic;
        rst   : std_logic;
    end record;

    type bram_port_out is
    record
        do  : std_logic_vector(31 downto 0);
        dop : std_logic_vector(3 downto 0);
    end record;
    
    type BRAMInArray is array (7 downto 0, 7 downto 0) of bram_port_in;
    type BRAMOutArray is array (7 downto 0, 7 downto 0) of bram_port_out;
    
    type PrefetcherCommand is
    record
        delay : integer range 0 to 2**9-1;
        pos : CameraCoordinate;
    end record;
    
end distorter_pkg;

package body distorter_pkg is
 
end distorter_pkg;
