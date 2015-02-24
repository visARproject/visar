library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


package simple_mac_pkg is

type PHYInInterface is record
    rst    : std_logic;

    gtxclk : std_logic;
    txd    : std_logic_vector(7 downto 0);
    txen   : std_logic;
    txer   : std_logic;
end record;
type PHYOutInterface is record
    txclk  : std_logic;

    rxd    : std_logic_vector(7 downto 0);
    rxdv   : std_logic;
    rxer   : std_logic;
    rxclk  : std_logic;
    col    : std_logic;
    cs     : std_logic;
end record;

type MACInInterface is record
    tx_flag : std_logic; -- needs to invert every time an entire packet is
                         -- available to be read. should start at 0 and
                         -- transition to 1 for first packet
    tx_data : std_logic_vector(7 downto 0);
    tx_eop  : std_logic;
end record;
type MACOutInterface is record
    tx_rd   : std_logic;
end record;


function mymax(left, right: integer) return integer is
begin
    if left > right then
        return left;
    else
        return right;
    end if;
end mymax;

function reverse_any_vector(a: in std_logic_vector) return std_logic_vector is
    variable result: std_logic_vector(a'RANGE);
    alias aa: std_logic_vector(a'REVERSE_RANGE) is a;
begin
    for i in aa'RANGE loop
        result(i) := aa(i);
    end loop;
    return result;
end;



end simple_mac_pkg;


package body simple_mac_pkg is

end simple_mac_pkg;
