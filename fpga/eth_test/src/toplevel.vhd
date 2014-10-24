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
    signal udp_tx_request, udp_tx_ready, udp_tx_almost_ready, udp_tx_wr_en, udp_data_end : std_logic;
    signal udp_data : std_logic_vector(31 downto 0);
    signal counter, next_counter : std_logic_vector(31 downto 0) := (others => '0');

    signal button_detect_reg : std_logic_vector(2 downto 0) := (others => '0');
    signal button_detect : std_logic;

    type state_t is (IDLE, REQ, SEND);
    signal state, next_state : state_t := IDLE;
    
    signal power_on_delay : unsigned(31 downto 0);
    signal go : std_logic := '0';

begin

    process(clk_62_5M, reset)
    begin
        if reset = '1' then
            go <= '0';
            power_on_delay <= to_unsigned(625_000_000, 32); -- 10 second at 62.5 MHz
        elsif rising_edge(clk_62_5M) then
            if power_on_delay = to_unsigned(0, 32) then
                go <= '1';
            else
                go <= '0';
                power_on_delay <= power_on_delay - 1;
            end if;
        end if;
    end process;

    button_detect <= '1';
    

    led(6) <= 'Z';

    reset <= not btn(0);


    seq : process(clk_62_5M, reset)
    begin
        if reset = '1' then
            state <= IDLE;
            counter <= (others => '0');
        elsif rising_edge(clk_62_5M) then
            state <= next_state;
            counter <= next_counter;
        end if;
    end process seq;

    comb : process(state, button_detect, udp_tx_ready, udp_tx_almost_ready)
    begin
        led(5 downto 0) <= (others => '0');
        next_counter <= counter;
        udp_data <= (others => '0');
        udp_tx_request <= '0';
        udp_tx_wr_en <= '0';
        udp_data_end <= '0';
        next_state <= state;
        case state is
            when IDLE =>
                led(0) <= '1';
                if button_detect = '1' then
                    next_state <= REQ;
                    udp_tx_request <= '1';
                end if;
            when REQ =>
                led(1) <= '1';
                udp_tx_request <= '1';
                if udp_tx_ready = '1' or udp_tx_almost_ready = '1' then
                    next_state <= SEND;
                end if;
            when SEND =>
                led(2) <= '1';
                udp_data <= counter;
                udp_tx_wr_en <= '1' and udp_tx_ready; -- Do NOT assert wr_en unless tx_ready is also true!
                udp_data_end <= '1';
                if udp_tx_ready = '1' then
                    next_state <= IDLE;
                    next_counter <= std_logic_vector(unsigned(counter) + 1);
                end if;
        end case;
    end process comb;


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
        
            udp_tx_request      => udp_tx_request,
            udp_tx_ready        => udp_tx_ready,
            udp_tx_almost_ready => udp_tx_almost_ready,
            udp_tx_wr_en        => udp_tx_wr_en,
            udp_data_in         => udp_data,
            udp_data_end        => udp_data_end);
        

end Behavioral;

