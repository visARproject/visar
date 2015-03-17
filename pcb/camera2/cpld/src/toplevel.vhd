library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

entity toplevel is
    port (
        baro_MISO:    in  std_logic;
        baro_MOSI:    out std_logic;
        baro_SCLK:    out std_logic;
        baro_spi_nCS: out std_logic := '1';
        
        C1_MISO:           in  std_logic;
        C1_monitor0:       in  std_logic;
        C1_monitor1:       in  std_logic;
        C1_MOSI:           out std_logic;
        C1_reset_n:        out std_logic := '0';
        C1_SCLK:           out std_logic;
        C1_ss_n:           out std_logic;
        C1_trigger0:       out std_logic := '0';
        C1_trigger1:       out std_logic := '0';
        C1_trigger2:       out std_logic := '0';
        C1_vcc1_8_en:      out std_logic := '0';
        C1_vcc3_0_main_en: out std_logic := '0';
        C1_vcc3_0_pix_en:  out std_logic := '0';
        
        C2_MISO:           in  std_logic;
        C2_monitor0:       in  std_logic;
        C2_monitor1:       in  std_logic;
        C2_MOSI:           out std_logic;
        C2_reset_n:        out std_logic := '0';
        C2_SCLK:           out std_logic;
        C2_ss_n:           out std_logic;
        C2_trigger0:       out std_logic := '0';
        C2_trigger1:       out std_logic := '0';
        C2_trigger2:       out std_logic := '0';
        C2_vcc1_8_en:      out std_logic := '0';
        C2_vcc3_0_main_en: out std_logic := '0';
        C2_vcc3_0_pix_en:  out std_logic := '0';
        
        imu_FSYNC:   out std_logic;
        imu_INT:     in  std_logic;
        imu_MISO:    in  std_logic;
        imu_MOSI:    out std_logic;
        imu_SCLK:    out std_logic;
        imu_spi_nCS: out std_logic := '1';
        
        pair7P:  inout std_logic;
        pair7N:  inout std_logic;
        pair8P:  inout std_logic;
        pair8N:  inout std_logic;
        pair9P:  inout std_logic;
        pair9N:  inout std_logic; -- GCK
        pair12P: inout std_logic; -- GCK
        pair12N: inout std_logic;
        pair13P: inout std_logic; -- GCK
        pair13N: inout std_logic;
        pair14P: inout std_logic;
        pair14N: inout std_logic;
        
        T1_master_clk: out   std_logic;
        T1_MISO:       in    std_logic;
        T1_MOSI:       out   std_logic;
        T1_pwr_dwn_l:  out   std_logic;
        T1_reset_l:    out   std_logic;
        T1_SCL:        inout std_logic;
        T1_SCLK:       out   std_logic;
        T1_SDA:        inout std_logic;
        T1_ss_n:       out   std_logic;
        
        T2_master_clk: out   std_logic;
        T2_MISO:       in    std_logic;
        T2_MOSI:       out   std_logic;
        T2_pwr_dwn_l:  out   std_logic;
        T2_reset_l:    out   std_logic;
        T2_SCL:        inout std_logic;
        T2_SCLK:       out   std_logic;
        T2_SDA:        inout std_logic;
        T2_ss_n:       out   std_logic);
end toplevel;

architecture arc of toplevel is
    signal MISO, MOSI, SCLK, nCS : std_logic;
    signal my_MISO : std_logic;
    signal data_in : std_logic_vector(9 downto 0);
    signal data_out : std_logic_vector(9 downto 0);
begin
    pair13N <= MISO;
    process (pair12P, pair13P) is
    begin
        if pair12P = '1' then
            SCLK <= '1';
        elsif pair13P = '1' then
            SCLK <= '0';
        end if;
    end process;
    MOSI <= pair14N;
    nCS  <= pair14P;
    
    pair8N <= C1_MISO;
    C1_MOSI <= MOSI;
    C1_SCLK <= SCLK;
    C1_ss_n <= pair7N;
    
    pair8P <= C2_MISO;
    C2_MOSI <= MOSI;
    C2_SCLK <= SCLK;
    C2_ss_n <= pair7P;
    
    process (nCS, SCLK) is
    begin
        if rising_edge(nCS) then
            if data_in(data_in'length-1) = '1' then
                C1_vcc1_8_en <= data_in(data_in'length-2);
                C1_vcc3_0_main_en <= data_in(data_in'length-3);
                C1_vcc3_0_pix_en <= data_in(data_in'length-4);
                C1_reset_n <= data_in(data_in'length-5);
                
                C2_vcc1_8_en <= data_in(data_in'length-6);
                C2_vcc3_0_main_en <= data_in(data_in'length-7);
                C2_vcc3_0_pix_en <= data_in(data_in'length-8);
                C2_reset_n <= data_in(data_in'length-9);
            end if;
        end if;
        
        if nCS = '1' then
            data_in <= (others => '0');
        elsif rising_edge(SCLK) then
            data_in <= data_in(data_in'length-2 downto 0) & MOSI;
        end if;
        
        if nCS = '1' then
            data_out <= "1010011001";
        elsif falling_edge(SCLK) then
            MISO <= data_out(data_out'length-1);
            data_out <= data_out(data_out'length-2 downto 0) & '-';
        end if;
    end process;
end arc;
