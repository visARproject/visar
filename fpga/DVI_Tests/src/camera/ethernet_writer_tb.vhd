library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;
use work.simple_mac_pkg.all;


entity camera_ethernet_writer_tb is
end entity camera_ethernet_writer_tb;

architecture RTL of camera_ethernet_writer_tb is
    signal clock  : std_logic := '0';
    
    signal ram_in  : ram_rd_port_in;
    signal ram_out : ram_rd_port_out;
    
    signal phy_in  : PHYInInterface;
    signal phy_out : PHYOutInterface;
begin
    clock <= not clock after 4 ns;
    
    U_ram_port : entity work.mock_ram_port port map (
        ram_in => ram_in,
        ram_out => ram_out);
    
    UUT : entity work.camera_ethernet_writer
        generic map (
            BUFFER_ADDRESS => 128)
        port map (
            ram_in => ram_in,
            ram_out => ram_out,
            clock_ethernet => clock,
            phy_in => phy_in,
            phy_out => phy_out);
end architecture RTL;
