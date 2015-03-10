library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity encode_10to9 is
    port (
        input  : in  std_logic_vector(9 downto 0);
        output : out std_logic_vector(8 downto 0)
    );
end entity encode_10to9;

architecture RTL of encode_10to9 is 
begin
    with input(9 downto 7) select output <=
        "00" & input(6 downto 0) when "000",
        "01" & input(6 downto 0) when "001",
        "10" & input(7 downto 1) when "01-",
        "11" & input(8 downto 2) when "1--";
end architecture RTL;
