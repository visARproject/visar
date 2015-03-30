library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity edid_wrapper is
    port(
        clock : in    std_logic;
        reset : in    std_logic;
        scl   : inout std_logic;
        sda   : inout std_logic
    );
end entity edid_wrapper;

architecture RTL of edid_wrapper is
    signal read_req, data_valid             : std_logic;
    signal data_to_master, data_from_master : std_logic_vector(7 downto 0);

    constant EDID_LENGTH : natural := 256;

    signal edid_index : std_logic_vector(7 downto 0) := (others => '0');
    type edid_t is array (0 to EDID_LENGTH - 1) of std_logic_vector(7 downto 0);
constant edid_data : edid_t := (x"00", x"ff", x"ff", x"ff", x"ff", x"ff", x"ff", x"00", x"3e", x"d2", x"03", x"00", x"00", x"00", x"00", x"00", x"0a", x"18", x"01", x"03", x"80", x"00", x"00", x"78", x"e2", x"60", x"b1", x"aa", x"55", x"40", x"b6", x"23", x"0c", x"50", x"54", x"00", x"00", x"00", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"01", x"40", x"29", x"38", x"3a", x"40", x"80", x"0d", x"70", x"21", x"0a", x"16", x"00", x"47", x"7e", x"00", x"00", x"00", x"1a", x"00", x"00", x"00", x"fc", x"00", x"52", x"69", x"66", x"74", x"20", x"44", x"4b", x"32", x"0a", x"20", x"20", x"20", x"20", x"00", x"00", x"00", x"ff", x"00", x"4d", x"53", x"43", x"45", x"34", x"38", x"30", x"37", x"4a", x"48", x"43", x"34", x"33", x"00", x"00", x"00", x"fd", x"00", x"38", x"4d", x"1e", x"96", x"11", x"00", x"0a", x"20", x"20", x"20", x"20", x"20", x"20", x"01", x"8e", x"02", x"03", x"04", x"03", x"40", x"29", x"38", x"3a", x"40", x"80", x"0d", x"70", x"21", x"0a", x"16", x"00", x"47", x"7e", x"00", x"00", x"00", x"1a", x"40", x"29", x"38", x"3a", x"40", x"80", x"0d", x"70", x"21", x"0a", x"16", x"00", x"47", x"7e", x"00", x"00", x"00", x"1a", x"40", x"29", x"38", x"3a", x"40", x"80", x"0d", x"70", x"21", x"0a", x"16", x"00", x"47", x"7e", x"00", x"00", x"00", x"1a", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"00", x"f0", x"5a", x"02");
begin
    U_I2C : entity work.I2C_slave
        generic map(SLAVE_ADDR => "1010000")
        port map(scl              => scl,
                 sda              => sda,
                 clk              => clock,
                 rst              => reset,
                 read_req         => read_req,
                 data_to_master   => data_to_master,
                 data_valid       => data_valid,
                 data_from_master => data_from_master);

    process (clock) is
    begin
        if rising_edge(clock) then
            if reset = '1' then
                edid_index <= (others => '0');
            else
                data_to_master <= edid_data(to_integer(unsigned(edid_index)));

                if data_valid = '1' then
                    edid_index <= data_from_master;
                elsif read_req = '1' then
                    edid_index <= std_logic_vector(unsigned(edid_index) + 1);
                end if;

            end if;
        end if;
    end process;

end architecture RTL;
