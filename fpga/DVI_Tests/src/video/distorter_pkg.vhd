library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

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
    
    subtype DistorterDelay is integer range 0 to 2**10-1;
    
    type PrefetcherCommand is
    record
        delay : DistorterDelay;
        pos   : CameraCoordinate; -- .x is real x / 3
    end record;
    
    function decode_9to10(input : std_logic_vector(8 downto 0)) return std_logic_vector is
    begin
        case input(8 downto 7) is
            when "00" =>
                return "000" & input(6 downto 0);
            when "01" =>
                return "001" & input(6 downto 0) ;
            when "10" =>
                return "01" & input(6 downto 0) & "1";
            when others =>
                return "1" & input(6 downto 0) & "11";
        end case;
    end decode_9to10;
    
    function linear10_to_sRGB(input : unsigned(9 downto 0)) return std_logic_vector is
    begin
        -- XXX make this actually do what it says it does
        return std_logic_vector(resize(input/4, 8));
    end;
end distorter_pkg;

package body distorter_pkg is
 
end distorter_pkg;
