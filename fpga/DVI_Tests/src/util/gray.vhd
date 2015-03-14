library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package util_gray is
    function binary_to_gray(x : unsigned) return std_logic_vector is
    begin
        return std_logic_vector(x srl 1) xor std_logic_vector(x);
    end binary_to_gray;
    
    function gray_to_binary(x : std_logic_vector) return unsigned is
        variable result : std_logic_vector(x'range);
    begin
        for i in x'high downto x'low loop
            if i = x'high then
                result(i) := x(i);
            else
                result(i) := x(i) xor result(i+1);
            end if;
        end loop;
        return unsigned(result);
    end gray_to_binary;
end package;
