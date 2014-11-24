library ieee;
library UNISIM;
use ieee.std_logic_1164.all;
use UNISIM.VComponents.all;
use work.video_bus.all;

entity dvi_transmitter is
    port (
        video_in     : in video_bus;
        tx_tmds     : out std_logic_vector(3 downto 0);
        tx_tmdsb    : out std_logic_vector(3 downto 0)
    );
end entity dvi_transmitter;
    
architecture RTL of dvi_transmitter is
    signal rst : std_logic;
    signal h_sync : std_logic;
    signal v_sync : std_logic;
    signal data_en : std_logic;
    
    signal tx0_clkfbout : std_logic;
    signal tx0_pllclk0  : std_logic;
    signal tx0_pllclk2  : std_logic;
    signal tx0_plllckd  : std_logic;
    signal tx0_clkfbin  : std_logic;
    signal tx0_pclk     : std_logic;
    signal tx0_pclkx2   : std_logic;
    signal tx0_pclkx10  : std_logic;
    signal tx0_bufpll_lock : std_logic;
    signal tx0_serdesstrobe : std_logic;
    signal tx0_reset : std_logic;
    
    
    -- Instantiate the verilog component here, since sigasi doesn't support multi-language projects.
    component dvi_encoder_top
        port(
            pclk : in std_logic;           
            pclkx2 : in std_logic;    
            pclkx10 : in std_logic;      
            serdesstrobe : in std_logic;
            rstin : in std_logic;
            blue_din : in std_logic_vector(7 downto 0);  
            green_din : in std_logic_vector(7 downto 0);
            red_din : in std_logic_vector(7 downto 0);
            hsync : in std_logic;
            vsync : in std_logic;
            de : in std_logic;    
            TMDS : out std_logic_vector(3 downto 0);
            TMDSB : out std_logic_vector(3 downto 0));
      end component;
    
begin
    rst <= not video_in.sync.valid;
    
    tx0_pclk <= video_in.sync.pixel_clk;
    
    U_SYNC_GEN : entity work.video_sync_gen
        port map(sync    => video_in.sync,
                 h_sync  => h_sync,
                 v_sync  => v_sync,
                 data_en => data_en);
                 
                 
    U_PLL_OSERDES_0 : component PLL_BASE
        generic map(CLKFBOUT_MULT         => 10,
                    CLKIN_PERIOD          => 10.0,
                    CLKOUT0_DIVIDE        => 1,
                    CLKOUT1_DIVIDE        => 10,
                    CLKOUT2_DIVIDE        => 5,
                    COMPENSATION          => "SOURCE_SYNCHRONOUS")
        port map(CLKFBOUT => tx0_clkfbout,
                 CLKOUT0  => tx0_pllclk0,
                 CLKOUT1  => open,
                 CLKOUT2  => tx0_pllclk2,
                 CLKOUT3  => open,
                 CLKOUT4  => open,
                 CLKOUT5  => open,
                 LOCKED   => tx0_plllckd,
                 CLKFBIN  => tx0_clkfbin,
                 CLKIN    => tx0_pclk,
                 RST      => rst);    
                 
                 
    U_tx0_clkfb_buf : component BUFG
        port map(O => tx0_clkfbin,
                 I => tx0_clkfbout);
                 
                
    U_tx0_pclkx2_buf : component BUFG
        port map(O => tx0_pclkx2,
                 I => tx0_pllclk2);
    
    
    U_tx0_ioclk_buf : component BUFPLL
        generic map(DIVIDE      => 5)
        port map(IOCLK        => tx0_pclkx10,
                 LOCK         => tx0_bufpll_lock,
                 SERDESSTROBE => tx0_serdesstrobe,
                 GCLK         => tx0_pclkx2,
                 LOCKED       => tx0_plllckd,
                 PLLIN        => tx0_pllclk0);
                 
    tx0_reset <= not tx0_bufpll_lock;
    
    U_dvi_tx : dvi_encoder_top
        port map(pclk         => tx0_pclk,
                 pclkx2       => tx0_pclkx2,
                 pclkx10      => tx0_pclkx10,
                 serdesstrobe => tx0_serdesstrobe,
                 rstin        => tx0_reset,
                 blue_din     => video_in.data.blue,
                 green_din    => video_in.data.green,
                 red_din      => video_in.data.red,
                 hsync        => h_sync,
                 vsync        => v_sync,
                 de           => data_en,
                 TMDS         => tx_tmds,
                 TMDSB        => tx_tmdsb);
        
    
end architecture RTL;
