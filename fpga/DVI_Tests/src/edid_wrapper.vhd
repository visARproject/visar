library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity edid_wrapper is
    port(
        clk_132MHz : in    std_logic;
        reset      : in    std_logic;
        scl        : inout std_logic;
        sda        : inout std_logic
    );
end entity edid_wrapper;

architecture RTL of edid_wrapper is
    signal read_req, data_valid             : std_logic;
    signal data_to_master, data_from_master : std_logic_vector(7 downto 0);

    constant EDID_LENGTH : natural := 256;

    signal edid_index : std_logic_vector(7 downto 0) := (others => '0');
    type edid_t is array (0 to EDID_LENGTH - 1) of std_logic_vector(7 downto 0);
    signal edid_data : edid_t := (      -- xxd -c1 ~/repos/visar/fpga/DK2.edid | cut -c10-12
        -- Begin Header --
        x"00",
        x"ff",
        x"ff",
        x"ff",
        x"ff",
        x"ff",
        x"ff",
        x"00",
        -- End Header --
        -- Begin Vendor / Product Identification --
        x"3e",                          -- ID Manufacturer Name --
        x"d2",                          -- ID Manufacturer Name --
        x"03",                          -- ID Product Code --
        x"00",                          -- ID Product Code --
        x"00",                          -- ID Serial Number --
        x"00",                          -- ID Serial Number --
        x"00",                          -- ID Serial Number --
        x"00",                          -- ID Serial Number --
        x"0a",                          -- Week of Manufacture --
        x"18",                          -- Year of Manufacture --
        -- End Vendor / Product Identification --
        -- Begin EDID Structure Version / Revision --
        x"01",                          -- Version # --
        x"03",                          -- Revision # --
        -- End EDID Structure Version / Revision --
        --Begin Basic Display Parameters / Features --
        x"80",                          -- Video Input Definition --
        x"00",                          -- Max. Horizontal Image Size --
        x"00",                          -- Max Vertical Image Size --
        x"78",                          -- Display Transfer Characteristic (Gamma) --
        x"e2",                          -- Feature Support --
        -- End Basic Display Parameters / Features --
        -- Begin Color Characteristics --
        x"60",                          -- Red/Green Low Bits --
        x"b1",                          -- Blue/White Low Bits --
        x"aa",                          -- Red-x --
        x"55",                          -- Red-y --
        x"40",                          -- Green-x --
        x"b6",                          -- Green-y --
        x"23",                          -- Blue-x --
        x"0c",                          -- Blue-y --
        x"50",                          -- White-x --
        x"54",                          -- White-y --
        -- End Color Characteristics --
        -- Begin Established Timings --
        x"00",                          -- Established Timings 1 --
        x"00",                          -- Established Timings 2 --
        x"00",                          -- Manufacturer's Reserved Timings --
        -- End Established Timings --
        -- Begin Standard Timing Identification --
        x"01",                          -- Standard Timing Identification #1 --
        x"01",                          -- Standard Timing Identification #1 --
        x"01",                          -- Standard Timing Identification #2 --
        x"01",                          -- Standard Timing Identification #2 --
        x"01",                          -- Standard Timing Identification #3 --
        x"01",                          -- Standard Timing Identification #3 --
        x"01",                          -- Standard Timing Identification #4 --
        x"01",                          -- Standard Timing Identification #4 --
        x"01",                          -- Standard Timing Identification #5 --
        x"01",                          -- Standard Timing Identification #5 --
        x"01",                          -- Standard Timing Identification #6 --
        x"01",                          -- Standard Timing Identification #6 --
        x"01",                          -- Standard Timing Identification #7 --
        x"01",                          -- Standard Timing Identification #7 --
        x"01",                          -- Standard Timing Identification #8 --
        x"01",                          -- Standard Timing Identification #8 --
        -- End Standard Timing Identification --
        -- Begin Detailed Timing Descriptions --
        -- Begin Detailed Timing Description #1 --
        x"8E",                          -- Pixel clock in 10 kHz units. (0.01–655.35 MHz, little-endian), lower byte -- 4072 = 164.98 MHz (checksum of original is 0x45) --
        x"33",                          -- Pixel clock in 10 kHz units. (0.01–655.35 MHz, little-endian), lower byte -- 338E = 131.90 MHz (checksum with this change is 0x36) --
        x"38",
        x"3a",
        x"40",
        x"80",
        x"0d",
        x"70",
        x"21",
        x"0a",
        x"16",
        x"00",
        x"47",
        x"7e",
        x"00",
        x"00",
        x"00",
        x"1a",
        -- End Detailed Timing Description #1 --
        -- Begin Detailed Timing Description #2 --
        x"00",
        x"00",
        x"00",
        x"fc", -- String Descriptor (EDID implementation guide section 3.7.6)
        x"00",
        x"52", -- ASCII R
        x"69", -- ASCII i
        x"66", -- ASCII f
        x"74", -- ASCII t
        x"20", -- ASCII Space
        x"44", -- ASCII D
        x"4b", -- ASCII K
        x"32", -- ASCII 2
        x"0a", -- ASCII Line Feed
        x"20", -- ASCII Space (required by specification to fill unused slots with space)
        x"20", -- ASCII Space
        x"20", -- ASCII Space
        x"20", -- ASCII Space
        -- End Detailed Timing Description #2 --
        -- Begin Detailed Timing Description #3 --
        x"00",
        x"00",
        x"00",
        x"ff",
        x"00",
        x"4d",
        x"53",
        x"43",
        x"45",
        x"34",
        x"38",
        x"30",
        x"37",
        x"4a",
        x"48",
        x"43",
        x"34",
        x"33",
        -- End Detailed Timing Description #3 --
        -- Begin Detailed Timing Description #4 --
        x"00",
        x"00",
        x"00",
        x"fd", -- Range Limits Descriptor (EDID implementation guide section 3.7.5)
        x"00", -- Minimum vertical field rate (Hz) --
        x"38", -- Maximum vertical field rate (Hz) --
        x"4d", -- Minimum horizontal field rate (Hz) --
        x"1e", -- Maximum horizontal field rate (Hz) --
        x"96", -- Maximum pixel clock rate x 10 MHz --
        x"11",
        x"00",
        x"0a",
        x"20",
        x"20",
        x"20",
        x"20",
        x"20",
        x"20",
        -- End Detailed Timing Description #4 --
        x"01", -- Extension Flag, 01 means 1 extension to follow --
        x"45", -- Checksum --
        -- Begin CEA EDID Timing Extension Version 3 block --
        x"02",
        x"03",
        x"04",
        x"03",
        x"8e",
        x"33",
        x"38",
        x"3a",
        x"40",
        x"80",
        x"0d",
        x"70",
        x"21",
        x"0a",
        x"16",
        x"00",
        x"47",
        x"7e",
        x"00",
        x"00",
        x"00",
        x"1a",
        x"de",
        x"3d",
        x"38",
        x"3a",
        x"40",
        x"80",
        x"0d",
        x"70",
        x"21",
        x"0a",
        x"16",
        x"00",
        x"47",
        x"7e",
        x"00",
        x"00",
        x"00",
        x"1a",
        x"d9",
        x"33",
        x"38",
        x"3a",
        x"40",
        x"b4",
        x"18",
        x"30",
        x"21",
        x"0a",
        x"c6",
        x"00",
        x"47",
        x"7e",
        x"00",
        x"00",
        x"00",
        x"1a",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"00",
        x"f0"
    );

begin
    U_I2C : entity work.I2C_slave
        generic map(SLAVE_ADDR => "1010000")
        port map(scl              => scl,
                 sda              => sda,
                 clk              => clk_132MHz,
                 rst              => reset,
                 read_req         => read_req,
                 data_to_master   => data_to_master,
                 data_valid       => data_valid,
                 data_from_master => data_from_master);

    process(clk_132MHz)
    begin
        if rising_edge(clk_132MHz) then
            if reset = '1' then
                edid_index <= (others => '0');
            else
                data_to_master <= edid_data(to_integer(unsigned(edid_index)));

                if data_valid = '1' then
                    edid_index <= data_from_master;
                elsif edid_index = std_logic_vector(to_unsigned(EDID_LENGTH - 1, edid_index'length)) then
                    edid_index <= (others => '0');
                elsif read_req = '1' then
                    edid_index <= std_logic_vector(unsigned(edid_index) + 1);
                end if;

            end if;
        end if;
    end process;

end architecture RTL;
