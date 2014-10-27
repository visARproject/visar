library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.simple_mac_pkg.all;

entity udp_wrapper is
    generic (
        SRC_MAC   : std_logic_vector(47 downto 0) := x"FFFFFFFFFFFF";
        DST_MAC   : std_logic_vector(47 downto 0) := x"FFFFFFFFFFFF";
        SRC_IP    : std_logic_vector(31 downto 0) := x"00000000"; -- 0.0.0.0
        DST_IP    : std_logic_vector(31 downto 0) := x"FFFFFFFF"; -- 255.255.255.255 
        SRC_PORT  : std_logic_vector(15 downto 0) := x"7A69";     -- 31337
        DST_PORT  : std_logic_vector(15 downto 0) := x"9001";     -- 36865
        DATA_SIZE : natural);
    port (
        clk_125M : in std_logic;
        reset    : in std_logic; -- must be synchronous to clk_125M

        -- PHY interface
        phy_in  : out PHYInInterface;
        phy_out : in  PHYOutInterface;

        -- not a MAC, but interface is the same
        data_in  : in  MACInInterface;
        data_out : out MACOutInterface);
end udp_wrapper;

architecture Behavioral of udp_wrapper is
    signal mac_in, next_mac_in : MACInInterface;
    signal mac_out : MACOutInterface;

    constant IP_SIZE : std_logic_vector(15 downto 0) := std_logic_vector(to_unsigned(20 + 8 + DATA_SIZE, 16));
    constant UDP_SIZE : std_logic_vector(15 downto 0) := std_logic_vector(to_unsigned(8 + DATA_SIZE, 16));
    constant PREPEND_LENGTH : natural := 42;
    
    type prepend_t is array (0 to PREPEND_LENGTH - 1) of std_logic_vector(7 downto 0);
    signal prepend_data : prepend_t := (
        --- Ethernet header ---
        SRC_MAC(47 downto 40), SRC_MAC(39 downto 32), SRC_MAC(31 downto 24), SRC_MAC(23 downto 16), SRC_MAC(15 downto 8), SRC_MAC(7 downto 0),
        DST_MAC(47 downto 40), DST_MAC(39 downto 32), DST_MAC(31 downto 24), DST_MAC(23 downto 16), DST_MAC(15 downto 8), DST_MAC(7 downto 0),
        x"08", x"00", -- Type (IP)
        --- IP header ---
        x"45", x"00", --  IPv4, IHL = 5, DSCP + ECN = 0
        IP_SIZE(15 downto 8), IP_SIZE(7 downto 0), -- IP Total Length
        x"00", x"00", -- identification = 0
        x"40", x"00", -- Flags + Fragment offset = 0x4000 (Don't Fragment, no fragment offset),
        x"40", x"11", -- TTL = 64 (0x40), IP Protocol: UDP (17, or 0x11)
        x"00", x"00", -- IP Checksum = 0
        SRC_IP(31 downto 24), SRC_IP(23 downto 16), SRC_IP(15 downto 8), SRC_IP(7 downto 0),
        DST_IP(31 downto 24), DST_IP(23 downto 16), DST_IP(15 downto 8), DST_IP(7 downto 0),
        --- UDP header ---
        SRC_PORT(15 downto 8), SRC_PORT(7 downto 0),
        DST_PORT(15 downto 8), DST_PORT(7 downto 0),
        UDP_SIZE(15 downto 8), UDP_SIZE(7 downto 0),
        x"00", x"00"); -- UDP Checksum = 0

    type tx_state_t is (TX_PREPEND, TX_PAYLOAD);
    signal state, next_state: tx_state_t := TX_PREPEND;

    subtype prepend_index_t is integer range 0 to PREPEND_LENGTH - 1;
    signal prepend_counter, next_prepend_counter : prepend_index_t := 0;
begin
    mac_in.tx_flag <= data_in.tx_flag;

    seq : process(clk_125M)
    begin
        if rising_edge(clk_125M) then
            if reset = '1' then
                state <= TX_PREPEND;
                prepend_counter <= 0;
                mac_in.tx_data <= (others => '-');
                mac_in.tx_eop <= '-';
            else
                state <= next_state;
                prepend_counter <= next_prepend_counter;
                mac_in.tx_data <= next_mac_in.tx_data;
                mac_in.tx_eop <= next_mac_in.tx_eop;
            end if;
        end if;
    end process seq;

    comb : process(state, mac_out, prepend_data, prepend_counter, data_in)
    begin
        next_state <= state;
        next_prepend_counter <= 0; -- prevent latches from being inferred
        next_mac_in.tx_eop <= mac_in.tx_eop;
        next_mac_in.tx_data <= mac_in.tx_data;
        data_out.tx_rd <= '0';

        if mac_out.tx_rd = '1' then
            case state is
                when TX_PREPEND =>
                    next_mac_in.tx_data <= prepend_data(prepend_counter);
                    next_mac_in.tx_eop <= '0';
                    next_prepend_counter <= prepend_counter + 1;
                    if prepend_counter = PREPEND_LENGTH - 1 then
                        next_state <= TX_PAYLOAD;
                        data_out.tx_rd <= '1';
                    end if;
                when TX_PAYLOAD =>
                    next_mac_in.tx_data <= data_in.tx_data;
                    next_mac_in.tx_eop <= data_in.tx_eop;
                    if data_in.tx_eop = '1' then
                        next_state <= TX_PREPEND;
                        next_prepend_counter <= 0;
                    else
                        data_out.tx_rd <= '1';
                    end if;
            end case;
        end if;
    end process comb;

    mac_inst : entity work.simple_mac
        port map (
            clk_125M => clk_125M,
            reset => reset,
            phy_in => phy_in,
            phy_out => phy_out,
            mac_in => mac_in,
            mac_out => mac_out);
end Behavioral;

