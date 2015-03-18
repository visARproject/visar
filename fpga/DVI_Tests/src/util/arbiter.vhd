library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.util_arbiter_pkg.all;


entity util_arbiter is
    generic (
        USERS : natural);
    port (
        clock : in std_logic;
        
        users_in  : in  ArbiterUserInArray (0 to USERS-1);
        users_out : out ArbiterUserOutArray(0 to USERS-1));
end entity;

architecture arc of util_arbiter is
    signal requests_synchronize_tmp : std_logic_vector(0 to USERS-1);
    signal requests_synchronized    : std_logic_vector(0 to USERS-1); -- requests synchronized into our clock domain
    
    signal enables : std_logic_vector(0 to USERS-1) := (others => '0');
    
    signal enables_ext_synchronize_tmp : std_logic_vector(0 to USERS-1);
    signal enables_ext_synchronized    : std_logic_vector(0 to USERS-1); -- enables synchronized into users' clock domains
    
    signal enables_synchronize_tmp : std_logic_vector(0 to USERS-1);
    signal enables_synchronized    : std_logic_vector(0 to USERS-1); -- enables_ext_synchronized resynchronized into our clock domain
begin
    process (clock, users_in) is
    begin
        -- synchronize requests into our clock domain
        if rising_edge(clock) then
            for i in 0 to USERS-1 loop
                requests_synchronize_tmp(i) <= users_in(i).request;
                requests_synchronized(i) <= requests_synchronize_tmp(i);
            end loop;
        end if;
        
        -- do actual arbitration (only effect is setting enables)
        if rising_edge(clock) then
            if enables = (enables'range => '0') then -- no enable is asserted
                if enables_synchronized /= (enables'range => '0') then -- synchronized enable is still asserted
                    -- do nothing, since we're waiting for an enable to finish deasserting
                elsif requests_synchronized /= (enables'range => '0') then -- at least one request is present
                    -- enable lowest request
                    for i in 0 to USERS-1 loop
                        if requests_synchronized(i) = '1' then
                            enables(i) <= '1';
                            exit;
                        end if;
                    end loop;
                end if;
            else -- some enable is already asserted
                if (enables and requests_synchronized) /= (enables'range => '0') then -- this request is still present
                    -- do nothing, since user still wants enable
                elsif (enables and enables_synchronized) = (enables'range => '0') then -- this request isn't in enables_synchronized
                    -- do nothing, since we're waiting for enable to finish asserting
                else
                    -- clear this enable
                    enables <= (others => '0'); -- (or all of them!)
                end if;
            end if;
        end if;
        
        -- synchronize enables into users' clock domains
        for i in 0 to USERS-1 loop
            if rising_edge(users_in(i).clock) then
                enables_ext_synchronize_tmp(i) <= enables(i);
                enables_ext_synchronized(i) <= enables_ext_synchronize_tmp(i);
            end if;
        end loop;
        
        -- resynchronize enables back into our clock domain
        if rising_edge(clock) then
            for i in 0 to USERS-1 loop
                enables_synchronize_tmp(i) <= enables_ext_synchronized(i);
                enables_synchronized(i) <= enables_synchronize_tmp(i);
            end loop;
        end if;
    end process;
    
    process (enables_ext_synchronized) is
    begin
        -- actually expose enables to users
        for i in 0 to USERS-1 loop
            users_out(i).enable <= enables_ext_synchronized(i);
        end loop;
    end process;
end architecture;
