library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.util_arbiter_pkg.all;


entity util_arbiter_tb is
end entity;

architecture arc of util_arbiter_tb is
    signal clock : std_logic := '0';
    
    constant USERS : natural := 2;
    
    signal users_in  : ArbiterUserInArray (0 to USERS-1) := (others => (clock => '0', request => '0'));
    signal users_out : ArbiterUserOutArray(0 to USERS-1);
begin
    UUT : entity work.util_arbiter
        generic map (
            USERS => USERS)
        port map (
            clock => clock,
            
            users_in  => users_in,
            users_out => users_out);
    
    clock <= not clock after 10 ns;
    
    users_in(0).clock <= not users_in(0).clock after 2 ns;
    
    users_in(1).clock <= not users_in(1).clock after 50 ns;
    
    process is
    begin
        wait for 1 us;
        
        users_in(0).request <= '1';
        
        wait for 1 us;
        
        users_in(0).request <= '0';
        
        wait for 1 us;
        
        users_in(0).request <= '1';
        
        wait for 1 us;
        
        users_in(1).request <= '1';
        
        wait for 1 us;
        
        users_in(0).request <= '0';
        
        wait for 1 us;
        
        users_in(1).request <= '0';
        
        wait;
    end process;
end architecture;
