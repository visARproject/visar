library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.simple_mac_pkg.all;

entity simple_mac is
    generic (
        IFG_LENGTH : integer := 12);
    port (
        clk_125M : in std_logic;
        reset    : in std_logic; -- must deassert synchronously to clk_125M

        -- PHY interface
        phy_in  : out PHYInInterface;
        phy_out : in  PHYOutInterface;

        -- MAC interface
        mac_in  : in  MACInInterface;
        mac_out : out MACOutInterface);
end simple_mac;


architecture Behavioral of simple_mac is
    signal tx_flag_sync1, tx_flag_sync2 : std_logic;
    signal last_tx_flag, next_last_tx_flag : std_logic;
    subtype FramesWaitingType is integer range 0 to 100;
    signal frames_waiting, next_frames_waiting : FramesWaitingType;
    
    constant PREAMBLE_LENGTH : integer := 7;
    type StateType is (
        IDLE, PREAMBLE, SFD, DATA, CRC1, CRC2, CRC3, CRC4, IFG);
    signal state, next_state: StateType;
    subtype CounterType is integer range 0 to
        mymax(IFG_LENGTH, PREAMBLE_LENGTH) - 1;
    signal counter, next_counter: CounterType;
    signal C, next_C : std_logic_vector(31 downto 0);
    signal next_phy_in : PHYInInterface;
begin
    process(clk_125M)
    begin
        if rising_edge(clk_125M) then
            tx_flag_sync1 <= mac_in.tx_flag;
            tx_flag_sync2 <= tx_flag_sync1;
        end if;
    end process;
    
    phy_in.rst <= reset;
    phy_in.gtxclk <= clk_125M;

    process(clk_125M)
    begin
        if rising_edge(clk_125M) then
            frames_waiting <= next_frames_waiting;
            state <= next_state;
            last_tx_flag <= next_last_tx_flag;
            counter <= next_counter;
            C <= next_C;
            phy_in.txd <= next_phy_in.txd;
            phy_in.txen <= next_phy_in.txen;
            phy_in.txer <= next_phy_in.txer;
        end if;
    end process;

    process(reset, state, counter, tx_flag_sync2, last_tx_flag, mac_in, frames_waiting, C, mac_in.tx_data)
        variable D : std_logic_vector(7 downto 0);
    begin
        D := mac_in.tx_data;
        
        next_frames_waiting <= frames_waiting;
        next_state <= state;
        next_counter <= 0; -- just to prevent inferring latches
        next_C <= (others => '-'); -- just to prevent inferring latches
        next_last_tx_flag <= last_tx_flag;
        next_phy_in.txd <= (others => '-');
        next_phy_in.txen <= '0';
        next_phy_in.txer <= '0';
        mac_out.tx_rd <= '0';
        if reset = '1' then
            next_frames_waiting <= 0;
            next_last_tx_flag <= '0';
            next_state <= IDLE;
        else
            if tx_flag_sync2 /= last_tx_flag then
                next_last_tx_flag <= not last_tx_flag;
                next_frames_waiting <= frames_waiting + 1;
            end if;
            
            if state = IDLE then
                if frames_waiting /= 0 and tx_flag_sync2 = last_tx_flag then
                    next_frames_waiting <= frames_waiting - 1;
                    next_state <= PREAMBLE;
                    next_counter <= 0;
                end if;
            elsif state = PREAMBLE then
                next_phy_in.txd <= x"55";
                next_phy_in.txen <= '1';
                if counter /= PREAMBLE_LENGTH - 1 then
                    next_counter <= counter + 1;
                else
                    next_state <= SFD;
                end if;
            elsif state = SFD then
                next_phy_in.txd <= x"D5";
                next_phy_in.txen <= '1';
                next_state <= DATA;
                mac_out.tx_rd <= '1';
                next_C <= x"FFFFFFFF";
            elsif state = DATA then
                next_phy_in.txd <= mac_in.tx_data;
                next_phy_in.txen <= '1';
                next_C(31) <= C(23) xor C(29) xor D(2);
                next_C(30) <= C(22) xor C(31) xor D(0) xor C(28) xor D(3);
                next_C(29) <= C(21) xor C(31) xor D(0) xor C(30) xor D(1) xor C(27) xor D(4);
                next_C(28) <= C(20) xor C(30) xor D(1) xor C(29) xor D(2) xor C(26) xor D(5);
                next_C(27) <= C(19) xor C(29) xor D(2) xor C(28) xor D(3) xor C(25) xor C(31) xor D(0) xor D(6);
                next_C(26) <= C(18) xor C(28) xor D(3) xor C(27) xor D(4) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(25) <= C(17) xor C(27) xor D(4) xor C(26) xor D(5);
                next_C(24) <= C(16) xor C(26) xor D(5) xor C(25) xor C(31) xor D(0) xor D(6);
                next_C(23) <= C(15) xor C(25) xor D(6) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(22) <= C(14) xor C(24) xor D(7);
                next_C(21) <= C(13) xor C(29) xor D(2);
                next_C(20) <= C(12) xor C(28) xor D(3);
                next_C(19) <= C(11) xor C(31) xor D(0) xor C(27) xor D(4);
                next_C(18) <= C(10) xor C(31) xor D(0) xor C(30) xor D(1) xor C(26) xor D(5);
                next_C(17) <= C(9) xor C(30) xor D(1) xor C(29) xor D(2) xor C(25) xor D(6);
                next_C(16) <= C(8) xor C(29) xor D(2) xor C(28) xor D(3) xor C(24) xor D(7);
                next_C(15) <= C(7) xor C(31) xor D(0) xor C(29) xor D(2) xor C(28) xor D(3) xor C(27) xor D(4);
                next_C(14) <= C(6) xor C(31) xor D(0) xor C(30) xor D(1) xor C(28) xor D(3) xor C(27) xor D(4) xor C(26) xor D(5);
                next_C(13) <= C(5) xor C(30) xor D(1) xor C(29) xor D(2) xor C(27) xor D(4) xor C(26) xor D(5) xor C(25) xor C(31) xor D(0) xor D(6);
                next_C(12) <= C(4) xor C(29) xor D(2) xor C(28) xor D(3) xor C(26) xor D(5) xor C(25) xor D(6) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(11) <= C(3) xor C(28) xor D(3) xor C(27) xor D(4) xor C(25) xor D(6) xor C(24) xor D(7);
                next_C(10) <= C(2) xor C(29) xor D(2) xor C(27) xor D(4) xor C(26) xor D(5) xor C(24) xor D(7);
                next_C(9) <= C(1) xor C(29) xor D(2) xor C(28) xor D(3) xor C(26) xor D(5) xor C(25) xor D(6);
                next_C(8) <= C(0) xor C(28) xor D(3) xor C(27) xor D(4) xor C(25) xor D(6) xor C(24) xor D(7);
                next_C(7) <= C(31) xor D(0) xor C(29) xor D(2) xor C(27) xor D(4) xor C(26) xor D(5) xor C(24) xor D(7);
                next_C(6) <= C(30) xor D(1) xor C(29) xor D(2) xor C(28) xor D(3) xor C(26) xor D(5) xor C(25) xor C(31) xor D(0) xor D(6);
                next_C(5) <= C(29) xor D(2) xor C(28) xor D(3) xor C(27) xor D(4) xor C(25) xor C(31) xor D(0) xor D(6) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(4) <= C(28) xor D(3) xor C(27) xor D(4) xor C(26) xor D(5) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(3) <= C(27) xor D(4) xor C(26) xor D(5) xor C(25) xor C(31) xor D(0) xor D(6);
                next_C(2) <= C(26) xor D(5) xor C(25) xor C(31) xor D(0) xor D(6) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(1) <= C(25) xor C(31) xor D(0) xor D(6) xor C(24) xor C(30) xor D(1) xor D(7);
                next_C(0) <= C(24) xor C(30) xor D(1) xor D(7);
                if mac_in.tx_eop = '1' then
                    next_state <= CRC1;
                else
                    mac_out.tx_rd <= '1';
                end if;
            elsif state = CRC1 then
                next_phy_in.txd <= not reverse_any_vector(C(31 downto 24));
                next_phy_in.txen <= '1';
                next_state <= CRC2;
                next_C <= C(23 downto 0) & "--------";
            elsif state = CRC2 then
                next_phy_in.txd <= not reverse_any_vector(C(31 downto 24));
                next_phy_in.txen <= '1';
                next_state <= CRC3;
                next_C <= C(23 downto 0) & "--------";
            elsif state = CRC3 then
                next_phy_in.txd <= not reverse_any_vector(C(31 downto 24));
                next_phy_in.txen <= '1';
                next_state <= CRC4;
                next_C <= C(23 downto 0) & "--------";
            elsif state = CRC4 then
                next_phy_in.txd <= not reverse_any_vector(C(31 downto 24));
                next_phy_in.txen <= '1';
                next_state <= IFG;
                next_counter <= 0;
            elsif state = IFG then
                if counter /= IFG_LENGTH - 1 then
                    next_counter <= counter + 1;
                else
                    next_state <= IDLE;
                end if;
            end if;
        end if;
    end process;
end Behavioral;
