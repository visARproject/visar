library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.all;

library unisim;
use unisim.vcomponents.all;

entity toplevel is
    port (
        clk: in std_logic;
        btn: in std_logic_vector(5 downto 0);
        led: out std_logic_vector(6 downto 0);
        
        phyrst: out std_logic;
        phytxclk: in std_logic;
        phyTXD: out std_logic_vector(7 downto 0);
        phytxen: out std_logic;
        phytxer: out std_logic;
        phygtxclk: out std_logic;
        phyRXD: in std_logic_vector(7 downto 0);
        phyrxdv: in std_logic;
        phyrxer: in std_logic;
        phyrxclk: in std_logic;
        phymdc: out std_logic;
        phymdi: inout std_logic;
        phyint: in std_logic; -- currently unused
        phycrs: in std_logic;
        phycol: in std_logic);
end toplevel;

architecture Behavioral of toplevel is
    signal reset : std_logic;
    signal clk_62_5M, clk_125M : std_logic;
    signal mdo, mdoen : std_logic;
    signal wr, sop, eop : std_logic;
    signal be : std_logic_vector(1 downto 0);
    signal data : std_logic_vector(31 downto 0);
    signal wa : std_logic;
    signal phygtxclk_int : std_logic;
    signal state : integer;
    signal state2 : std_logic_vector(31 downto 0);
    signal counter : std_logic_vector(31 downto 0);
begin
    reset <= not btn(0);

    clockgeninst : entity work.clk_wiz_v3_6
        port map (
            CLK_IN1 => clk,
            CLK_OUT1 => clk_125M,
            CLK_OUT2 => clk_62_5M);

    state2 <= std_logic_vector(to_unsigned(state, 32));
    led <= state2(25 downto 19);
    
    sender : process(clk_62_5M, reset)
    begin
        if rising_edge(clk_62_5M) and wa = '1' then
            wr <= '0';
            sop <= '0';
            eop <= '0';
            be <= "00";
            state <= state + 1;
            if reset = '1' or state < 0 then
                state <= 0;
            elsif state >= 100 and state <= 199 then
                wr <= '1';
                data <= not "00000000000000000000000000000000";
                if state = 100 then
                    sop <= '1';
                end if;
                if state = 199 then
                    eop <= '1';
                    data <= counter;
                    counter <= std_logic_vector(unsigned(counter) + 1);
                end if;
            elsif state >= 300-1 then
                state <= 0;
            end if;
        end if;
    end process;

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

