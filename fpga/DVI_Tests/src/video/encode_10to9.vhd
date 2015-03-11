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

    process(input) is
    begin
        if input(9) = '1' then
            output <= "11" & input(8 downto 2);
        elsif input(8) = '1' then
            output <= "10" & input(7 downto 1);
        elsif input(7) = '1' then
            output <= "01" & input(6 downto 0);
        else
            output <= "00" & input(6 downto 0);
        end if;
    end process;

end architecture RTL;
