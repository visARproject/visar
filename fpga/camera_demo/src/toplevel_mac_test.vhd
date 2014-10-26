library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.all;

library unisim;
use unisim.vcomponents.all;

use work.simple_mac_pkg.all;

entity toplevel_mac_test is
    port (
        CLK_I: in std_logic;
        RESET_I: in std_logic;
        
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
end toplevel_mac_test;

architecture Behavioral of toplevel_mac_test is
    signal CLK_I_buf : std_logic;
    signal clk_125M : std_logic;
    
    signal phy_in : PHYInInterface;
    signal phy_out : PHYOutInterface;
    signal mac_in : MACInInterface;
    signal mac_out : MACOutInterface;
    signal phygtxclk_int : std_logic;

    signal reset, reset_buf : std_logic;
    subtype PosType is integer range 0 to 1000;
    signal pos, pos2 : PosType;
    
    signal din : std_logic_vector(35 downto 0);
    signal wr_en : std_logic;
    
    signal dout : std_logic_vector(8 downto 0);
begin
    phyrst <= not phy_in.rst;
    phytxd <= phy_in.txd;
    phytxen <= phy_in.txen;
    phytxer <= phy_in.txer;
    
    i_oddr : oddr2
        generic map (
            ddr_alignment => "c1",    -- sets output alignment to "none", "c0", "c1"
            init          => '0',     -- sets initial state of the q output to '0' or '1'
            srtype        => "async"  -- specifies "sync" or "async" set/reset
        ) port map (
            q  => phygtxclk,
            c0 => phy_in.gtxclk,
            c1 => not phy_in.gtxclk,
            ce => '1',
            d0 => '0',
            d1 => '1',
            r  => '0',
            s  => '0');
    
    phymdc <= '0';
    phymdi <= 'Z';
    
    mac_inst : entity work.simple_mac
        port map (
            clk_125M => clk_125M,
            reset => reset,
            phy_in => phy_in,
            phy_out => phy_out,
            mac_in => mac_in,
            mac_out => mac_out);

    seq : process(clk_125M, reset)
    begin
        if rising_edge(clk_125M) then
            reset_buf <= not RESET_I;
            reset <= reset_buf;
        end if;
    end process seq;

   IBUFG_inst : IBUFG
   port map (
      O => CLK_I_buf, -- Clock buffer output
      I => CLK_I  -- Clock buffer input (connect directly to top-level port)
   );

    Inst_dcm_fixed : entity work.dcm_fixed
      port map
       (-- Clock in ports
        CLK_IN1            => CLK_I_buf,
        -- Clock out ports
        CLK_OUT1           => open,
        CLK_OUT2           => open,
        CLK_OUT3           => clk_125M,
        CLK_OUT4           => open,
        -- Status and control signals
        RESET              => '0',
        LOCKED             => open);

    mymacfifo : entity work.macfifo
      PORT MAP (
        rst => reset,
        wr_clk => clk_125M,
        rd_clk => clk_125M,
        din => din,
        wr_en => wr_en,
        rd_en => mac_out.tx_rd,
        dout => dout);
    mac_in.tx_eop <= dout(8);
    mac_in.tx_data <= dout(7 downto 0);
    
    dataproducer : process(clk_125M)
    begin
        if rising_edge(clk_125M) then
            wr_en <= '0';
            din <= (others => '-');
            if reset = '1' then
                pos <= 0;
                pos2 <= 0;
                mac_in.tx_flag <= '0';
            elsif pos = 999 then
                wr_en <= '1';
                pos <= 0;
                if pos2 = 19 then
                    din <= "011111111011111111011111111111111111";
                    mac_in.tx_flag <= not mac_in.tx_flag;
                    pos2 <= 0;
                else
                    din <= "011111111011111111011111111011111111";
                    pos2 <= pos2 + 1;
                end if;
            else
                pos <= pos + 1;
            end if;
        end if;
    end process;
end Behavioral;

