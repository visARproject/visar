library ieee;
library unisim;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use unisim.VComponents.all;
use work.video_bus.all;

entity dvi_receiver is
	port (
		rst : in std_logic;
		rx_tmds : in std_logic_vector(3 downto 0);
		rx_tmdsb: in std_logic_vector(3 downto 0);
		video_output : out video_bus);
end entity dvi_receiver;

architecture RTL of dvi_receiver is
	
	signal tmdsclk_p : std_logic;--   (RX0_TMDS[3]),
    signal tmdsclk_n : std_logic;--   (RX0_TMDSB[3]),
    signal blue_p    : std_logic;--  (RX0_TMDS[0]),
    signal green_p   : std_logic;--  (RX0_TMDS[1]),
    signal red_p     : std_logic;--  (RX0_TMDS[2]),
    signal blue_n    : std_logic;--  (RX0_TMDSB[0]),
    signal green_n   : std_logic;--  (RX0_TMDSB[1]),
    signal red_n     : std_logic;--  (RX0_TMDSB[2]),
    signal extrst    : std_logic;--  (~rstbtn_n),
    signal rxclkint  : std_logic;
    signal rxclk	 : std_logic;
    signal clkfbout  : std_logic;
    signal pllclk0   : std_logic;
    signal pllclk1   : std_logic;
    signal pllclk2   : std_logic;
    signal pll_lckd  : std_logic;
    signal pclk  	 : std_logic;
    signal pclkx2    : std_logic;
    signal bufpll_lock : std_logic;
    signal pclkx10 	 : std_logic;
    signal intrst 	 : std_logic;
    signal serdesstrobe : std_logic;
    signal blue_vld, green_vld, red_vld : std_logic;
    signal blue_rdy, green_rdy, red_rdy : std_logic;
    signal blue_psalgnerr, green_psalgnerr, red_psalgnerr : std_logic;
    signal data_enable_blue, data_enable_green, data_enable_red : std_logic;
    
    signal hsync, hsync_prev, vsync, vsync_prev : std_logic;
    
    signal h_cnt, v_cnt : unsigned(11 downto 0);
    
    component decode 
    port(
    	reset : in std_logic;            --
		pclk : in std_logic;             --  pixel clock
		pclkx2 : in std_logic;           --  double pixel rate for gear box
		pclkx10 : in std_logic;          --  IOCLK
		serdesstrobe : in std_logic;     --  serdesstrobe for iserdes2
		din_p : in std_logic;            --  data from dvi cable
		din_n : in std_logic;            --  data from dvi cable
		other_ch0_vld : in std_logic;    --  other channel0 has valid data now
		other_ch1_vld : in std_logic;    --  other channel1 has valid data now
		other_ch0_rdy : in std_logic;    --  other channel0 has detected a valid starting pixel
		other_ch1_rdy : in std_logic;    --  other channel1 has detected a valid starting pixel
		iamvld : out std_logic;           --  I have valid data now
		iamrdy : out std_logic;           --  I have detected a valid new pixel
		psalgnerr : out std_logic;        --  Phase alignment error
		c0 : out std_logic;
		c1 : out std_logic;
		de : out std_logic;     
		sdout : out std_logic_vector(9 downto 0);
		dout : out std_logic_vector(7 downto 0));
    end component;
    
begin
	extrst 		<= rst;
	tmdsclk_p 	<= rx_tmds(3);
	tmdsclk_n 	<= rx_tmdsb(3);
	blue_p    	<= rx_tmds(0);
	blue_n		<= rx_tmdsb(0);
	green_p 	<= rx_tmds(1);
	green_n 	<= rx_tmdsb(1);
	red_p 		<= rx_tmds(2);
	red_n 		<= rx_tmdsb(2);
	
	
	ibuf_rxclk : component IBUFDS
		generic map(DIFF_TERM   => false,
					IOSTANDARD  => "TMDS_33")
		port map(O  => rxclkint,
			     I  => tmdsclk_p,
			     IB => tmdsclk_n);
	
	bufio_tmdsclk : component BUFIO2
		generic map(DIVIDE_BYPASS => true,
			        DIVIDE        => 1)
		port map(DIVCLK       => rxclk,
			     IOCLK        => open,
			     SERDESSTROBE => open,
			     I            => rxclkint);

-- I don't believe this is necessary	     
--	tmdsclk_bufg : component BUFG
--		port map(O => tmdsclk,
--			     I => rxclk);
			     
	PLL_ISERDES : component PLL_BASE
		generic map(CLKFBOUT_MULT         => 10,
			        CLKIN_PERIOD          => 10.0,
			        CLKOUT0_DIVIDE        => 1,
			        CLKOUT1_DIVIDE        => 10,
			        CLKOUT2_DIVIDE        => 5,
			        COMPENSATION          => "INTERNAL")
		port map(CLKFBOUT => clkfbout,
			     CLKOUT0  => pllclk0,
			     CLKOUT1  => pllclk1,
			     CLKOUT2  => pllclk2,
			     CLKOUT3  => open,
			     CLKOUT4  => open,
			     CLKOUT5  => open,
			     LOCKED   => pll_lckd,
			     CLKFBIN  => clkfbout,
			     CLKIN    => rxclk,
			     RST      => extrst);
			     
	video_output.sync.valid <= pll_lckd;

	pclkbufg : component BUFG
		port map(O => pclk,
			     I => pllclk1);		
			     
	pclkx2bufg : component BUFG
		port map(O => pclkx2,
			     I => pllclk2);	     

	intrst <= not bufpll_lock;

	ioclk_buf : component BUFPLL
		generic map(DIVIDE      => 5)
		port map(IOCLK        => pclkx10,
			     LOCK         => bufpll_lock,
			     SERDESSTROBE => serdesstrobe,
			     GCLK         => pclkx2,
			     LOCKED       => pll_lckd,
			     PLLIN        => pllclk0);
			     
			     
	blue_decoder : decode
		port map(reset         => intrst,
			     pclk          => pclk,
			     pclkx2        => pclkx2,
			     pclkx10       => pclkx10,
			     serdesstrobe  => serdesstrobe,
			     din_p         => blue_p,
			     din_n         => blue_n,
			     other_ch0_vld => green_vld,
			     other_ch1_vld => red_vld,
			     other_ch0_rdy => green_rdy,
			     other_ch1_rdy => red_rdy,
			     iamvld        => blue_vld,
			     iamrdy        => blue_rdy,
			     psalgnerr     => blue_psalgnerr,
			     c0            => hsync,
			     c1            => vsync,
			     de            => data_enable_blue,
			     sdout         => open,
			     dout          => video_output.data.blue);
			     
	green_decoder : decode
		port map(reset         => intrst,
			     pclk          => pclk,
			     pclkx2        => pclkx2,
			     pclkx10       => pclkx10,
			     serdesstrobe  => serdesstrobe,
			     din_p         => green_p,
			     din_n         => green_n,
			     other_ch0_vld => blue_vld,
			     other_ch1_vld => red_vld,
			     other_ch0_rdy => blue_rdy,
			     other_ch1_rdy => red_rdy,
			     iamvld        => green_vld,
			     iamrdy        => green_rdy,
			     psalgnerr     => green_psalgnerr,
			     c0            => open,
			     c1            => open,
			     de            => data_enable_green,
			     sdout         => open,
			     dout          => video_output.data.green);
			     
	red_decoder : decode
		port map(reset         => intrst,
			     pclk          => pclk,
			     pclkx2        => pclkx2,
			     pclkx10       => pclkx10,
			     serdesstrobe  => serdesstrobe,
			     din_p         => red_p,
			     din_n         => red_n,
			     other_ch0_vld => blue_vld,
			     other_ch1_vld => green_vld,
			     other_ch0_rdy => blue_rdy,
			     other_ch1_rdy => green_rdy,
			     iamvld        => red_vld,
			     iamrdy        => red_rdy,
			     psalgnerr     => red_psalgnerr,
			     c0            => open,
			     c1            => open,
			     de            => data_enable_red,
			     sdout         => open,
			     dout          => video_output.data.red);
			     
			     
	video_output.sync.pixel_clk <= pclk;

	-- Derive the frame reset from hsync and vsync
	process(pclk)
	begin		
		if rising_edge(pclk) then
            if h_cnt /= H_MAX - 1 then
                h_cnt <= h_cnt + 1;
            else
                h_cnt <= to_unsigned(0, h_cnt'length);
                if v_cnt /= V_MAX - 1 then
                    v_cnt <= v_cnt + 1;
                else
                    v_cnt <= to_unsigned(0, v_cnt'length);
                end if;
            end if;
			
			-- Synchronization
			hsync_prev <= hsync;	
			vsync_prev <= vsync;
			
			if hsync_prev = '1' and hsync = '0' then
				h_cnt <= to_unsigned(HSYNC_END + 1, h_cnt'length); 
			end if;
			
			if vsync_prev = '0' and vsync = '1' then
				v_cnt <= to_unsigned(VSYNC_END + 1, v_cnt'length);
			end if;			
		end if;			
	end process;
	
	process(h_cnt, v_cnt)
	begin
        video_output.sync.frame_rst <= '0';
        if h_cnt = H_MAX - 1 and v_cnt = V_MAX - 1 then
            video_output.sync.frame_rst <= '1';
        end if;
    end process;
	

end architecture RTL;
