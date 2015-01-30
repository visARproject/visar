library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.camera.all;

entity camera_wrapper is
    port (
        clock_310MHz : in std_logic;
        reset        : in std_logic;
        
        camera_out : out camera_out;
        camera_in  : in  camera_in;
        
        output : out camera_output);
end camera_wrapper;

architecture arc of camera_wrapper is
    signal clock_out : std_logic;
    signal sync, data0, data1, data2, data3, clock : std_logic;
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
    
    SYNC_IBUF : IBUFDS_DIFF_OUT
        generic map (
            IOSTANDARD => "LVDS_33",
            DIFF_TERM  => TRUE)
        port map (
            I  => camera_in.sync_p,
            IB => camera_in.sync_n,
            O  => sync);
    DATA0_IBUF : IBUFDS_DIFF_OUT
        generic map (
            IOSTANDARD => "LVDS_33",
            DIFF_TERM  => TRUE)
        port map (
            I  => camera_in.data0_p,
            IB => camera_in.data0_n,
            O  => data0);
    DATA1_IBUF : IBUFDS_DIFF_OUT
        generic map (
            IOSTANDARD => "LVDS_33",
            DIFF_TERM  => TRUE)
        port map (
            I  => camera_in.data1_p,
            IB => camera_in.data1_n,
            O  => data1);
    DATA2_IBUF : IBUFDS_DIFF_OUT
        generic map (
            IOSTANDARD => "LVDS_33",
            DIFF_TERM  => TRUE)
        port map (
            I  => camera_in.data2_p,
            IB => camera_in.data2_n,
            O  => data2);
    DATA3_IBUF : IBUFDS_DIFF_OUT
        generic map (
            IOSTANDARD => "LVDS_33",
            DIFF_TERM  => TRUE)
        port map (
            I  => camera_in.data3_p,
            IB => camera_in.data3_n,
            O  => data3);
    CLOCK_IBUF : IBUFDS_DIFF_OUT
        generic map (
            IOSTANDARD => "LVDS_33",
            DIFF_TERM  => TRUE)
        port map (
            I  => camera_in.clock_p,
            IB => camera_in.clock_n,
            O  => clock);
end architecture;
