library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package util_gray is
    function binary_to_gray(x : unsigned) return std_logic_vector is
    begin
        return std_logic_vector(x srl 1) xor std_logic_vector(x);
    end binary_to_gray;
end package;
