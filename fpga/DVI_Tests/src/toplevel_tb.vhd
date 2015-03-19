library ieee;
use ieee.std_logic_1164.all;

library unisim;
use unisim.vcomponents.all;


use work.camera_pkg.all;


entity toplevel_tb is
end entity toplevel_tb;



architecture RTL of toplevel_tb is
    signal clk_100MHz         : std_logic := '0';
    signal rst_n              : std_logic;
    signal tx_tmds, rx_tmds   : std_logic_vector(3 downto 0);
    signal tx_tmdsb, rx_tmdsb : std_logic_vector(3 downto 0);
    signal uart_rx            : std_logic;
    
    signal reset : std_logic;
    signal ready : std_logic;
    signal data  : std_logic_vector(7 downto 0);
    signal write : std_logic;
    
    signal mcb3_dram_dq     : std_logic_vector(16-1 downto 0);
    signal mcb3_dram_a      : std_logic_vector(13-1 downto 0);
    signal mcb3_dram_ba     : std_logic_vector(3-1 downto 0);
    signal mcb3_dram_ras_n  : std_logic;
    signal mcb3_dram_cas_n  : std_logic;
    signal mcb3_dram_we_n   : std_logic;
    signal mcb3_dram_odt    : std_logic;
    signal mcb3_dram_cke    : std_logic;
    signal mcb3_dram_dm     : std_logic;
    signal mcb3_dram_udqs   : std_logic;
    signal mcb3_dram_udqs_n : std_logic;
    signal mcb3_rzq         : std_logic;
    signal mcb3_zio         : std_logic;
    signal mcb3_dram_udm    : std_logic;
    signal mcb3_dram_dqs    : std_logic;
    signal mcb3_dram_dqs_n  : std_logic;
    signal mcb3_dram_ck     : std_logic;
    signal mcb3_dram_ck_n   : std_logic;
    
    signal mcb3_command : std_logic_vector(2 downto 0);
    signal mcb3_enable1 : std_logic;
    signal mcb3_enable2 : std_logic;
    
    signal mcb3_dram_dqs_vector   : std_logic_vector(1 downto 0);
    signal mcb3_dram_dqs_n_vector : std_logic_vector(1 downto 0);
    signal mcb3_dram_dm_vector    : std_logic_vector(1 downto 0);
    
    signal rdqs_n : std_logic_vector(1 downto 0);
    
    signal right_camera_in  : camera_in;
    signal right_camera_out : camera_out;
begin
    UUT : entity work.toplevel port map(
        clk_100MHz => clk_100MHz,
        rst_n      => rst_n,
        rx_tmds    => rx_tmds,
        rx_tmdsb   => rx_tmdsb,
        tx_tmds    => tx_tmds,
        tx_tmdsb   => tx_tmdsb,

        mcb3_dram_dq     => mcb3_dram_dq,
        mcb3_dram_a      => mcb3_dram_a,
        mcb3_dram_ba     => mcb3_dram_ba,
        mcb3_dram_ras_n  => mcb3_dram_ras_n,
        mcb3_dram_cas_n  => mcb3_dram_cas_n,
        mcb3_dram_we_n   => mcb3_dram_we_n,
        mcb3_dram_odt    => mcb3_dram_odt,
        mcb3_dram_cke    => mcb3_dram_cke,
        mcb3_dram_dm     => mcb3_dram_dm,
        mcb3_dram_udqs   => mcb3_dram_udqs,
        mcb3_dram_udqs_n => mcb3_dram_udqs_n,
        mcb3_rzq         => mcb3_rzq,
        mcb3_zio         => mcb3_zio,
        mcb3_dram_udm    => mcb3_dram_udm,
        mcb3_dram_dqs    => mcb3_dram_dqs,
        mcb3_dram_dqs_n  => mcb3_dram_dqs_n,
        mcb3_dram_ck     => mcb3_dram_ck,
        mcb3_dram_ck_n   => mcb3_dram_ck_n,

        uart_rx    => uart_rx,
        
        phytxclk => 'U',
        phyRXD => (others => 'U'),
        phyrxdv => 'U',
        phyrxer => 'U',
        phyrxclk => 'U',
        phyint => 'U',
        phycrs => 'U',
        phycol => 'U',
        
        left_camera_in   => (others => 'U'),
        right_camera_in  => right_camera_in,
        right_camera_out => right_camera_out);
    
    UART : entity work.uart_transmitter
        generic map (
            CLOCK_FREQUENCY => 100.0e6,
            BAUD_RATE => 4000000.0)
        port map (
            clock => clk_100MHz,
            reset => reset,
            tx    => uart_rx,
            ready => ready,
            data  => data,
            write => write);
    
    clk_100MHz <= not clk_100MHz after 5 ns;
    
    process is
        constant sync_data : std_logic_vector(19 downto 0) := "1110100110" & "0000110101";
        --constant data_data : std_logic_vector(19 downto 0);
    begin
        while true loop
            for i in 0 to sync_data'length-1 loop
                wait until right_camera_out.clock_p'event;
                right_camera_in.sync_p <= not sync_data(sync_data'length-1-i);
                right_camera_in.sync_n <=     sync_data(sync_data'length-1-i);
            end loop;
        end loop;
    end process;
    
    process
    begin
        write <= '0';
        
        reset <= '1';
        wait for 1 us;
        reset <= '0';
        wait for 400 us;
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"da";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"01";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"01";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"23";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"45";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"67";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        
        
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"da";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"01";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"04";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"89";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"ab";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"cd";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"ef";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"da";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"01";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"23";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"45";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"67";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"da";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"04";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"00";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"89";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"ab";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"cd";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait until rising_edge(clk_100MHz) and ready = '1';
        write <= '1';
        data <= x"ef";
        wait until rising_edge(clk_100MHz); write <= '0';
        
        wait;
    end process;        
    
    rst_n <= not reset;  
              
               
    mcb3_command <= (mcb3_dram_ras_n & mcb3_dram_cas_n & mcb3_dram_we_n);

    process(mcb3_dram_ck)
    begin
      if (rising_edge(mcb3_dram_ck)) then
        if false then --if (c3_sys_rst = '0') then
          mcb3_enable1   <= '0';
          mcb3_enable2 <= '0';
        elsif (mcb3_command = "100") then
          mcb3_enable2 <= '0';
        elsif (mcb3_command = "101") then
          mcb3_enable2 <= '1';
        else
          mcb3_enable2 <= mcb3_enable2;
        end if;
        mcb3_enable1     <= mcb3_enable2;
      end if;
    end process;
-----------------------------------------------------------------------------
--read
-----------------------------------------------------------------------------
    mcb3_dram_dqs_vector(1 downto 0)               <= (mcb3_dram_udqs & mcb3_dram_dqs)
                                                           when (mcb3_enable2 = '0' and mcb3_enable1 = '0')
							   else "ZZ";
    mcb3_dram_dqs_n_vector(1 downto 0)             <= (mcb3_dram_udqs_n & mcb3_dram_dqs_n)
                                                           when (mcb3_enable2 = '0' and mcb3_enable1 = '0')
							   else "ZZ";
    
-----------------------------------------------------------------------------
--write
-----------------------------------------------------------------------------
    mcb3_dram_dqs          <= mcb3_dram_dqs_vector(0)
                              when ( mcb3_enable1 = '1') else 'Z';

    mcb3_dram_udqs          <= mcb3_dram_dqs_vector(1)
                              when (mcb3_enable1 = '1') else 'Z';


     mcb3_dram_dqs_n        <= mcb3_dram_dqs_n_vector(0)
                              when (mcb3_enable1 = '1') else 'Z';
    mcb3_dram_udqs_n         <= mcb3_dram_dqs_n_vector(1)
                              when (mcb3_enable1 = '1') else 'Z';

   
   
mcb3_dram_dm_vector <= (mcb3_dram_udm & mcb3_dram_dm);

     u_mem_c3 : entity work.ddr2_model_c3 port map(
        ck        => mcb3_dram_ck,
        ck_n      => mcb3_dram_ck_n,
        cke       => mcb3_dram_cke,
        cs_n      => '0',
        ras_n     => mcb3_dram_ras_n,
        cas_n     => mcb3_dram_cas_n,
        we_n      => mcb3_dram_we_n,
        dm_rdqs   => mcb3_dram_dm_vector ,
        ba        => mcb3_dram_ba,
        addr      => mcb3_dram_a,
        dq        => mcb3_dram_dq,
        dqs       => mcb3_dram_dqs_vector,
        dqs_n     => mcb3_dram_dqs_n_vector,
        rdqs_n    => rdqs_n,
        odt       => mcb3_dram_odt
      );
  
   zio_pulldown3 : PULLDOWN port map(O => mcb3_zio);
   rzq_pulldown3 : PULLDOWN port map(O => mcb3_rzq);
end architecture RTL;
