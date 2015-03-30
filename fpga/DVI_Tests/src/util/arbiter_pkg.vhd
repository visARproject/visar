library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


package util_arbiter_pkg is

    type ArbiterUserIn is
    record
        clock   : std_logic;
        request : std_logic;
    end record;
    type ArbiterUserInArray is array(natural range <>) of ArbiterUserIn;

    type ArbiterUserOut is
    record
        enable : std_logic;
    end record;
    type ArbiterUserOutArray is array(natural range <>) of ArbiterUserOut;
    
end util_arbiter_pkg;

package body util_arbiter_pkg is
end util_arbiter_pkg;
