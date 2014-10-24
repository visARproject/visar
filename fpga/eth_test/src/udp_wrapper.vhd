library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.all;
use IEEE.MATH_REAL.all;

library unisim;
use unisim.vcomponents.all;

entity udp_wrapper is
    generic (
        SRC_MAC  : std_logic_vector(47 downto 0) := x"FFFFFFFFFFFF";
        DST_MAC  : std_logic_vector(47 downto 0) := x"FFFFFFFFFFFF";
        ETH_PAYLOAD_SIZE : std_logic_vector(15 downto 0) := x"05DC"; -- 1500 byte payload for all frames
        SRC_IP   : std_logic_vector(31 downto 0) := x"00000000";     -- 0.0.0.0
        DST_IP   : std_logic_vector(31 downto 0) := x"FFFFFFFF";     -- 255.255.255.255 
        SRC_PORT : std_logic_vector(15 downto 0) := x"7A69";         -- 31337
        DST_PORT : std_logic_vector(15 downto 0) := x"9001";         -- 36865
        UDP_PAYLOAD_SIZE : std_logic_vector(15 downto 0) := x"05C8" -- 1480 (1500 - 20 bytes for IP header)
    );
    port (
        clk_125M  : in std_logic;
        clk_62_5M : in std_logic;
        reset     : in std_logic;
        -- PHY interface
        phyrst    : out std_logic;
        phytxclk  : in std_logic;
        phyTXD    : out std_logic_vector(7 downto 0);
        phytxen   : out std_logic;
        phytxer   : out std_logic;
        phygtxclk : out std_logic;
        phyRXD    : in std_logic_vector(7 downto 0);
        phyrxdv   : in std_logic;
        phyrxer   : in std_logic;
        phyrxclk  : in std_logic;
        phymdc    : out std_logic;
        phymdi    : inout std_logic;
        phyint    : in std_logic; -- currently unused
        phycrs    : in std_logic;
        phycol    : in std_logic;
        
        -- UDP data interface
        udp_tx_request      : in  std_logic; -- when high, move from idle state to transmitting header info, then assert ready
        udp_tx_ready        : out std_logic; -- when high, we are ready for the client to send us data
        udp_tx_almost_ready : out std_logic; -- asserted when we're transmitting the last word of the prepended header
        udp_tx_wr_en        : in  std_logic; -- the client asserts this to write to the MAC FIFO
        udp_data_in         : in  std_logic_vector(31 downto 0);
        udp_data_end        : in  std_logic
);
end udp_wrapper;

architecture Behavioral of udp_wrapper is

    signal mdo, mdoen : std_logic;
    signal wr, sop, eop : std_logic;
    signal be : std_logic_vector(1 downto 0);
    signal data : std_logic_vector(31 downto 0);
    signal wa : std_logic;
    signal phygtxclk_int : std_logic;

    constant PREPEND_LENGTH : natural := 11;
    
    type prepend_t is array (0 to PREPEND_LENGTH - 1) of std_logic_vector(31 downto 0);

    signal prepend_word : prepend_t := (--- Ethernet ---                               -- Capital: dst mac; lower: src mac
                                        SRC_MAC(47 downto 16),                         -- AA BB CC DD
                                        SRC_MAC(15 downto  0) & DST_MAC(47 downto 32), -- EE FF aa bb
                                        DST_MAC(31 downto  0),                         -- cc dd ee ff
                                        --- IP, except for Type ---
                                        x"0800" & x"45" & x"00",                       -- Type (IP), IPv4, IHL = 5, DSCP + ECN = 0
                                        ETH_PAYLOAD_SIZE & x"0000",                    -- IP Total Length (default to 1500), identification = 0
                                        x"4000" & x"40" & x"11",                       -- Flags + Fragment offset = 0x4000 (Don't Fragment, no fragment offset),
                                                                                       --    TTL = 64 (0x40), IP Protocol: UDP (17, or 0x11)
                                        x"0000" & SRC_IP(31 downto 16),                -- IP Checksum = 0, first half of source IP
                                        SRC_IP(15 downto 0) & DST_IP(31 downto 16),    -- Second half of source IP, first half of dest IP
                                        --- UDP, except for second half of dest IP ---
                                        DST_IP(15 downto 0) & SRC_PORT,                -- Second half of dest IP, source UDP port
                                        DST_PORT & UDP_PAYLOAD_SIZE,                    -- Dest UDP port, UDP length
                                        x"0000" & x"0000"                              -- UDP Checksum = 0, pad with two bytes
                                       );

    type tx_state_t is (IDLE, TX_PREPEND, TX_PAYLOAD);
    signal state, next_state: tx_state_t := IDLE;

    constant COUNTER_WIDTH : integer := integer(ceil(log2(real(PREPEND_LENGTH)))); 
    subtype prepend_index_t is integer range 0 to PREPEND_LENGTH - 1;
    signal prepend_counter, next_prepend_counter : prepend_index_t := 0;

begin

    seq : process(clk_62_5M, reset)
    begin
        if rising_edge(clk_62_5M) then
            if reset = '1' then
                state <= IDLE;
                prepend_counter <= 0;
            else
                state <= next_state;
                prepend_counter <= next_prepend_counter;
            end if;
        end if;
    end process seq;

    comb : process(state, udp_tx_request, wa, prepend_counter, prepend_word, udp_data_in, udp_tx_wr_en)
    begin
        udp_tx_ready <= '0';
        udp_tx_almost_ready <= '0';
        wr <= '0';
        sop <= '0';
        eop <= '0';
        be <= "00";
        data <= (others => '0');
        next_prepend_counter <= prepend_counter;

        case state is
            when IDLE =>
                if udp_tx_request = '1' and wa = '1' then
                    next_state <= TX_PREPEND;
                else
                    next_state <= state;
                end if;
            when TX_PREPEND =>
                data <= prepend_word(prepend_counter);
                if wa = '1' then
                    wr <= '1';
                    if prepend_counter = 0 then
                        sop <= '1';
                    end if;
                    if prepend_counter >= PREPEND_LENGTH - 1 then
                        next_prepend_counter <= 0;
                        next_state <= TX_PAYLOAD;
                    else
                        next_prepend_counter <= prepend_counter + 1;
                        next_state <= state;
                    end if;
                    if prepend_counter = PREPEND_LENGTH - 1 then
                        udp_tx_almost_ready <= '1';
                    end if;
                end if;
            when TX_PAYLOAD =>
                udp_tx_ready <= wa;
                wr <= udp_tx_wr_en;
                data <= udp_data_in;
                if udp_data_end = '1' then
                    eop <= '1';
                    next_state <= IDLE;
                else 
                    next_state <= state;
                end if;
            when others => null;
        end case;
    end process comb;

    ethmac : entity work.MAC_top
        port map (
            Reset => reset,
            Clk_125M => clk_125M,
            Clk_user => clk_62_5M,
            Clk_reg => clk_62_5M,
            
            Rx_mac_rd => '0',
            Tx_mac_wa => wa,
            Tx_mac_wr => wr,
            Tx_mac_data => data,
            Tx_mac_BE => be,
            Tx_mac_sop => sop,
            Tx_mac_eop => eop,
            Pkg_lgth_fifo_rd => '0',
            CSB => '1',
            WRB => '1',
            CD_in => "0000000000000000",
            CA => "00000000",
            
            Gtx_clk => phygtxclk_int,
            Rx_clk => phyrxclk,
            Tx_clk => phytxclk,
            Tx_er => phytxer,
            Tx_en => phytxen,
            Txd => phyTXD,
            Rx_er => phyrxer,
            Rx_dv => phyrxdv,
            Rxd => phyRXD,
            Crs => phycrs,
            Col => phycol,
            
            Mdo => mdo,
            MdoEn => mdoen,
            Mdi => phymdi,
            Mdc => phymdc);


    phymdi <= mdo when mdoen = '1' else 'Z';
    phyrst <= not reset;
    
    i_oddr : oddr2
        generic map (
            ddr_alignment => "c1",    -- sets output alignment to "none", "c0", "c1"
            init          => '0',     -- sets initial state of the q output to '0' or '1'
            srtype        => "async"  -- specifies "sync" or "async" set/reset
        ) port map (
            q  => phygtxclk,
            c0 => phygtxclk_int,
            c1 => not phygtxclk_int,
            ce => '1',
            d0 => '0',
            d1 => '1',
            r  => '0',
            s  => '0');
end Behavioral;

