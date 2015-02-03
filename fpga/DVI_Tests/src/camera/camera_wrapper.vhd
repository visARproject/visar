library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.camera.all;

entity camera_wrapper is
    port (
        clock_620MHz : in std_logic;
        clock_310MHz : in std_logic;
        clock_124MHz : in std_logic;
        clock_locked : in std_logic;
        reset        : in std_logic;
        
        camera_out : out camera_out;
        camera_in  : in  camera_in;
        
        output : out camera_output);
end camera_wrapper;

architecture arc of camera_wrapper is
    signal clock_out : std_logic;
    
    signal deserializer_clock : std_logic;
    signal deserializer_out   : std_logic_vector(24 downto 0);
begin
    CLOCK_OUT_DDR : ODDR2
        generic map (
            DDR_ALIGNMENT => "NONE",
            INIT          => '0',
            SRTYPE        => "SYNC")
        port map (
            Q  => clock_out,
            C0 => clock_310MHz,
            C1 => not clock_310MHz,
            CE => '1',
            D0 => '1',
            D1 => '0',
            R  => '0',
            S  => '0');
    CLOCK_OUT_OBUF : OBUFDS
        generic map (
            IOSTANDARD => "LVDS_33")
        port map (
            I  => clock_out,
            O  => camera_out.clock_p,
            OB => camera_out.clock_n);
    
    deserializer_clock <= clock_124MHz;
    DESERIALIZER : entity work.camera_deserializer port map (
        IO_RESET => reset,
        
        CLK_IN => clock_620MHz,
        CLK_DIV_IN => clock_124MHz,
        LOCKED_IN => clock_locked,
        DATA_IN_FROM_PINS_P => camera_in.sync_p & camera_in.data0_p &
            camera_in.data1_p & camera_in.data2_p & camera_in.data3_p,
        DATA_IN_FROM_PINS_N => camera_in.sync_n & camera_in.data0_n &
            camera_in.data1_n & camera_in.data2_n & camera_in.data3_n,
        
        LOCKED_OUT => open,
        DATA_IN_TO_DEVICE => deserializer_out,
        BITSLIP => '0',
        
        DEBUG_IN => "00",
        DEBUG_OUT => open);
    
    output.clock <= deserializer_clock;
    output.data <= deserializer_out;
end architecture;
