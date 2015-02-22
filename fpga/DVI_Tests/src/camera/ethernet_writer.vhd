library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

use work.camera.all;
use work.ram_port.all;
use work.simple_mac_pkg.all;

entity camera_ethernet_writer is
    generic (
        BUFFER_ADDRESS : in integer); -- needs to be 4-byte aligned
    port (
        ram_in  : out ram_rd_port_in;
        ram_out : in  ram_rd_port_out;
        
        clock_ethernet : std_logic; -- must be 125MHz
        
        phy_in  : out PHYInInterface;
        phy_out : in  PHYOutInterface);
end entity;

architecture arc of camera_ethernet_writer is
    constant BURST_LENGTH_WORDS : integer := RAM_FIFO_LENGTH/4; -- 4-byte words
    constant BURST_LENGTH_BYTES : integer := BURST_LENGTH_WORDS * 4;
    constant DATA_SIZE : integer := 1024; -- bytes
    constant PAYLOAD_SIZE : integer := 4 + DATA_SIZE; -- bytes
    constant COUNT : integer := 2048; -- packets
    
    signal clock : std_logic;
    
    signal packet_index : integer range 0 to COUNT-1 := 0;
    signal state : integer range 0 to 1 := 0;
    signal read_index : integer range 0 to DATA_SIZE/BURST_LENGTH_BYTES := 0;
    signal words_in_flight : integer range 0 to 2*RAM_FIFO_LENGTH-1 := 0;
    signal words_committed : integer range 0 to 1+DATA_SIZE/4 := 0;
    
    signal fifo_write_enable : std_logic := '0';
    signal fifo_write_data   : std_logic_vector(35 downto 0);
    signal fifo_write_full   : std_logic;
    
    signal fifo_read_data : std_logic_vector(8 downto 0);
    
    signal tx_flag : std_logic := '0';
    
    signal data_in  : MACInInterface;
    signal data_out : MACOutInterface;
begin
    assert DATA_SIZE mod BURST_LENGTH_BYTES = 0;
    
    clock <= clock_ethernet;
    
    ram_in.cmd.clk <= clock;
    ram_in.rd.clk <= clock;
    process (words_in_flight, read_index, packet_index, clock, state, fifo_write_full, ram_out, words_committed) is
    begin
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        
        fifo_write_enable <= '0';
        fifo_write_data <= (others => '-');
        ram_in.rd.en <= '0';
        if state = 0 then
            if fifo_write_full = '0' then
                fifo_write_enable <= '1';
                fifo_write_data <= "0" & "00000000" & "0" & "00000000" & "0" & std_logic_vector(to_unsigned(packet_index/256, 8)) & "0" & std_logic_vector(to_unsigned(packet_index mod 256, 8));
                if rising_edge(clock) then
                    state <= 1;
                end if;
            end if;
        elsif state = 1 then
            if words_in_flight <= RAM_FIFO_LENGTH/2 and read_index /= DATA_SIZE/BURST_LENGTH_BYTES then
                ram_in.cmd.en <= '1';
                ram_in.cmd.instr <= READ_PRECHARGE_COMMAND;
                ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(BUFFER_ADDRESS + DATA_SIZE * packet_index + BURST_LENGTH_BYTES * read_index, ram_in.cmd.byte_addr'length));
                ram_in.cmd.bl <= std_logic_vector(to_unsigned(BURST_LENGTH_WORDS-1, ram_in.cmd.bl'length));
                if rising_edge(clock) then
                    words_in_flight <= words_in_flight + BURST_LENGTH_WORDS;
                    read_index <= read_index + 1;
                end if;
            elsif fifo_write_full = '0' then
                if ram_out.rd.empty = '0' then
                    fifo_write_enable <= '1';
                    fifo_write_data <= "0" & ram_out.rd.data(31 downto 24) & "0" & ram_out.rd.data(23 downto 16) & "0" & ram_out.rd.data(15 downto 8) & "0" & ram_out.rd.data(7 downto 0);
                    if words_committed = DATA_SIZE/4-1 then
                        fifo_write_data(8) <= '1'; -- end of packet
                    end if;
                    ram_in.rd.en <= '1';
                    if rising_edge(clock) then
                        words_in_flight <= words_in_flight - 1;
                        if words_committed = DATA_SIZE/4-1 then
                            tx_flag <= not tx_flag;
                            if packet_index /= COUNT-1 then
                                packet_index <= packet_index + 1;
                            else
                                packet_index <= 0;
                            end if;
                            read_index <= 0;
                            state <= 0;
                        end if;
                        words_committed <= words_committed + 1;
                    end if;
                end if;
            end if;
        end if;
    end process;
    
    FIFO : entity work.util_fifo_narrowed
        generic map (
            WIDTH => 36,
            LOG_2_DEPTH => integer(ceil(log2(real(PAYLOAD_SIZE/4)*1.5))),
            WRITE_WIDTH => 36,
            READ_WIDTH => 9)
        port map (
            write_clock  => clock,
            write_enable => fifo_write_enable,
            write_data   => fifo_write_data,
            write_full   => fifo_write_full,
            
            read_clock => clock_ethernet,
            read_enable => data_out.tx_rd,
            read_data => fifo_read_data,
            read_empty => open);
    data_in.tx_data <= fifo_read_data(7 downto 0);
    data_in.tx_eop  <= fifo_read_data(8);
    data_in.tx_flag <= tx_flag;
    
    U_UDP : entity work.udp_wrapper
        generic map(
            SRC_MAC   => x"000000000000",
            DST_MAC   => x"00249b09740d",
            SRC_IP    => x"00000000", -- 0.0.0.0
            DST_IP    => x"FFFFFFFF", -- 255.255.255.255
            SRC_PORT  => x"0000",
            DST_PORT  => x"1441",
            DATA_SIZE => PAYLOAD_SIZE)
        port map(
            clk_125M => clock_ethernet,
            reset    => '0',
            phy_in   => phy_in,
            phy_out  => phy_out,
            data_in  => data_in,
            data_out => data_out);
end architecture;