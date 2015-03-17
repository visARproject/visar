library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

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
    
    function decode_9to10(input : std_logic_vector(8 downto 0)) return unsigned is
    begin
        case input(8 downto 7) is
            when "00" =>
                return unsigned("000" & input(6 downto 0));
            when "01" =>
                return unsigned("001" & input(6 downto 0));
            when "10" =>
                return unsigned("01" & input(6 downto 0) & "1");
            when others =>
                return unsigned("1" & input(6 downto 0) & "11");
        end case;
    end decode_9to10;
    
    function encode_10to9(input : unsigned(9 downto 0)) return std_logic_vector is
    begin
        if input(9) = '1' then
            return "11" & std_logic_vector(input(8 downto 2));
        elsif input(8) = '1' then
            return "10" & std_logic_vector(input(7 downto 1));
        elsif input(7) = '1' then
            return "01" & std_logic_vector(input(6 downto 0));
        else
            return "00" & std_logic_vector(input(6 downto 0));
        end if;
    end encode_10to9;
    
    
    type sRGBLookupType is array (0 to 2**10-1) of std_logic_vector(7 downto 0);
    
    function compute_sRGB_lookup return sRGBLookupType is
        variable linear, sRGB : real;
        variable result : sRGBLookupType;
        constant a : real := 0.055;
    begin
        for i in sRGBLookupType'range loop
            linear := real(i)/1023.0;
            if linear <= 0.0031308 then
                sRGB := 12.92 * linear;
            else
                sRGB := (1.0+a) * linear**(1.0/2.4) - a;
            end if;
            result(i) := std_logic_vector(to_unsigned(integer(round(255.0*sRGB)), 8));
        end loop;
        return result;
    end compute_sRGB_lookup;
    
    constant sRGB_lookup : sRGBLookupType := compute_sRGB_lookup;
    
    function linear10_to_sRGB(input : unsigned(9 downto 0)) return std_logic_vector is
    begin
        return sRGB_lookup(to_integer(input));
    end;
end distorter_pkg;

package body distorter_pkg is
 
end distorter_pkg;
