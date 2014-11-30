library ieee;
use ieee.std_logic_1164.all;

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
    
end distorter_pkg;

package body distorter_pkg is
 
end distorter_pkg;
