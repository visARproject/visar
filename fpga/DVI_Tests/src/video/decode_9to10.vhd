library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity decode_9to10 is
    port(
        input  : in  std_logic_vector(8 downto 0);
        output : out std_logic_vector(9 downto 0)
    );
end entity decode_9to10;

architecture RTL of decode_9to10 is
begin
    with input(8 downto 7) select output <=
        "000" & input(6 downto 0) when "00",
        "001" & input(6 downto 0) when "01",
        "01" & input(6 downto 0) & "1" when "10",
        "1" & input(6 downto 0) & "11" when "11";
end architecture RTL;
