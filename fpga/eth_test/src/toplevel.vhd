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
    signal udp_tx_request, udp_tx_ready, udp_tx_wr_en, udp_data_end : std_logic;
    signal udp_data : std_logic_vector(31 downto 0);
    signal counter : std_logic_vector(31 downto 0);
    
    signal button_detect_reg : std_logic_vector(2 downto 0) := (others => '0');
    signal button_detect : std_logic;
    
    type state_t is (IDLE, REQ, SEND);
    signal state : state_t := IDLE;
     
     signal delay_counter, reset_counter : std_logic_vector(31 downto 0); -- how long should I delay? 1 second at 62.5 MHz is 62.5 million counts
    signal go : std_logic;
     
begin
    delay1 : process(clk_62_5M, reset)
     begin
         if reset = '1' then
              delay_counter <= std_logic_vector(to_unsigned(62_500_000, 32));
                button_detect <= '0';
          elsif rising_edge(clk_62_5M) then
              if delay_counter = x"00000000" then
                   button_detect <= '1';
                else
                   delay_counter <= std_logic_vector(unsigned(delay_counter) - 1);
                    button_detect <= '0';
                end if;
        
          end if;
     end process delay1;
     
     delay2 : process(clk_62_5M, reset)
     begin
         if reset = '1' then
              reset_counter <= std_logic_vector(to_unsigned(625_000_000, 32));
                go <= '0';
          elsif rising_edge(clk_62_5M) then
              if reset_counter = x"00000000" then
                   go <= '1';
                else
                   reset_counter <= std_logic_vector(unsigned(reset_counter) - 1);
                    go <= '0';
                end if;
        
          end if;
     end process delay2;
     
     led(6) <= 'Z';
     
    reset <= not btn(0);

    process(clk_62_5M)
    begin
        button_detect_reg(2 downto 1) <= button_detect_reg(1 downto 0);
        button_detect_reg(0) <= btn(1);
 --       button_detect <= button_detect_reg(2) xor button_detect_reg(1);
    end process;
--    button_detect <= '1';  
    traffic_gen : process(clk_62_5M, reset)
    begin
        if reset = '1' or go = '0' then
            led(5 downto 0) <= (others => '0');
            counter <= (others => '0');
            udp_data <= (others => '0');
            udp_tx_request <= '0';
            udp_tx_wr_en <= '0';
            udp_data_end <= '0';
            state <= IDLE;
        elsif rising_edge(clk_62_5M) then
              led(5 downto 0) <= (others => '0');
            udp_tx_request <= '0';
            udp_tx_wr_en <= '0';
            udp_data_end <= '0';
            case state is
                when IDLE =>
                         led(0) <= '1';
                    if button_detect = '1' then
                        state <= REQ;
                        udp_tx_request <= '1';
                    else
                        state <= state;
                    end if;
                when REQ =>
                         led(1) <= '1';
                    udp_tx_request <= '1';
                    if udp_tx_ready = '1' then
                        state <= SEND;
                    else
                        state <= state;
                    end if;
                when SEND =>
                         led(2) <= '1';
                    udp_data <= counter;
-- TODO: is it bad to assume that asserting the MAC's write enable signal (wr) when the write available ("ready") signal (wa) is false will cause no harm? 
--       how does their fifo work?
                    udp_tx_wr_en <= '1'; 
                    udp_data_end <= '1';
                    if udp_tx_ready = '1' then
                        state <= IDLE;
                        counter <= std_logic_vector(unsigned(counter) + 1);
                    else
                        state <= state;
                    end if;
            end case;

        end if;
    end process traffic_gen;
    
    
    clockgeninst : entity work.clk_wiz_v3_6
        port map (
            CLK_IN1 => clk, -- 100 MHz input
            CLK_OUT1 => clk_125M,
            CLK_OUT2 => clk_62_5M);

    udp : entity work.udp_wrapper
        generic map (
            SRC_MAC          => x"FFFFFFFFFFFF",
            DST_MAC          => x"FFFFFFFFFFFF",
            ETH_PAYLOAD_SIZE => x"05DC",         -- 1500 byte payload for all frames
            SRC_IP           => x"00000000",     -- 0.0.0.0
            DST_IP           => x"FFFFFFFF",     -- 255.255.255.255 
            SRC_PORT         => x"7A69",         -- 31337
            DST_PORT         => x"9001",         -- 36865
            UDP_PAYLOAD_SIZE => x"05C8")          -- 1480 (1500 - 20 bytes for IP header) 
        port map (
            clk_125M  => clk_125M,
            clk_62_5M => clk_62_5M,
            reset     => reset,
        
            phyrst    => phyrst,
            phytxclk  => phytxclk,
            phyTXD    => phyTXD,
            phytxen   => phytxen,
            phytxer   => phytxer,
            phygtxclk => phygtxclk,
            phyRXD    => phyRXD,
            phyrxdv   => phyrxdv,
            phyrxer   => phyrxer,
            phyrxclk  => phyrxclk,
            phymdc    => phymdc,
            phymdi    => phymdi,
            phyint    => phyint,
            phycrs    => phycrs,
            phycol    => phycol,
        
            udp_tx_request  => udp_tx_request,
            udp_tx_ready    => udp_tx_ready,
            udp_tx_wr_en    => udp_tx_wr_en,
            udp_data_in     => udp_data,
            udp_data_end    => udp_data_end);
        
          
          
          
end Behavioral;

