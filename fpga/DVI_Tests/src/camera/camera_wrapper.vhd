library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

library digilent;
use digilent.all;

use work.camera.all;

entity camera_wrapper is
    port (
        clock_24MHz     : in std_logic;
        reset           : in std_logic;
        
        camera_out    : out   camera_out;
        camera_inout  : inout camera_inout;
        camera_vdd_en : out std_logic;
        
        output : out camera_output);
end camera_wrapper;

architecture arc of camera_wrapper is
    signal camera_data_in_S : std_logic_vector(7 downto 0);
    signal camera_pclk_in_S : std_logic;
    signal camera_fv_in_S   : std_logic;
    signal camera_lv_in_S   : std_logic;
    
    signal dummy_t : std_logic;

    attribute S : string;
    --attribute S of camera_inout : signal is "TRUE";
    attribute S of dummy_t : signal is "TRUE";
begin

    --------------------------
    -- Camera A interface
    --------------------------
    U_CAMERA : entity work.CamCtl
        port map(D_O     => output.data, -- 8 bit data coming out of the cameras
                 PCLK_O  => output.clock, -- Pixel clk coming 
                 DV_O    => output.data_valid,
                 RST_I   => reset,
                 CLK     => clock_24MHz,
                 SDA     => camera_inout.sda,
                 SCL     => camera_inout.scl,
                 D_I     => camera_data_in_S,
                 PCLK_I  => camera_pclk_in_S,
                 MCLK_O  => camera_out.mclk,
                 LV_I    => camera_lv_in_S,
                 FV_I    => camera_fv_in_S,
                 RST_O   => camera_out.rst,
                 PWDN_O  => camera_out.pwdn,
                 VDDEN_O => camera_vdd_en);

    -- Workaround for IN_TERM bug AR#     40818
    -- Effectively, for any inout used, you have to use these
    --    IOBUFs to turn the inout into an input
    U_IOBUF_CAMERA_DATA : for i in 7 downto 0 generate
        U_IOBUF_CAMERA_DATA : IOBUF
            generic map(
                DRIVE      => 12,
                IOSTANDARD => "DEFAULT",
                SLEW       => "SLOW")
            port map(
                O  => camera_data_in_S(i), -- Buffer output
                IO => camera_inout.data(i), -- Buffer inout port (connect directly to top-level port)
                I  => '0',              -- Buffer input
                T  => dummy_t               -- 3-state enable input, high=input, low=output
            );
    end generate;
    U_IOBUF_CAMERA_PCLK : IOBUF
        generic map(
            DRIVE      => 12,
            IOSTANDARD => "DEFAULT",
            SLEW       => "SLOW")
        port map(
            O  => camera_pclk_in_S,   -- Buffer output
            IO => camera_inout.pclk,  -- Buffer inout port (connect directly to top-level port)
            I  => '0',                  -- Buffer input
            T  => dummy_t                   -- 3-state enable input, high=input, low=output
        );
    U_IOBUF_CAMERA_FV : IOBUF
        generic map(
            DRIVE      => 12,
            IOSTANDARD => "DEFAULT",
            SLEW       => "SLOW")
        port map(
            O  => camera_fv_in_S,     -- Buffer output
            IO => camera_inout.fv,    -- Buffer inout port (connect directly to top-level port)
            I  => '0',                  -- Buffer input
            T  => dummy_t                   -- 3-state enable input, high=input, low=output
        );
    U_IOBUF_CAMERA_LV : IOBUF
        generic map(
            DRIVE      => 12,
            IOSTANDARD => "DEFAULT",
            SLEW       => "SLOW")
        port map(
            O  => camera_lv_in_S,     -- Buffer output
            IO => camera_inout.lv,    -- Buffer inout port (connect directly to top-level port)
            I  => '0',                  -- Buffer input
            T  => dummy_t                   -- 3-state enable input, high=input, low=output
        );
    dummy_t <= '1';
    --------------------------
    
    output.frame_valid <= camera_fv_in_S;
end architecture;
