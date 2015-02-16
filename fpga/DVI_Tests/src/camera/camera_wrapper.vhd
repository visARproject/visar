library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

use work.camera.all;

entity camera_wrapper is
    generic (
        SYNC_INVERTED  : boolean;
        DATA3_INVERTED : boolean;
        DATA2_INVERTED : boolean;
        DATA1_INVERTED : boolean;
        DATA0_INVERTED : boolean);
    port (
        clock_camera_unbuf  : in std_logic;
        clock_camera_over_2 : in std_logic;
        clock_camera_over_5 : in std_logic;
        clock_locked        : in std_logic;
        reset               : in std_logic;
        
        camera_out : out camera_out;
        camera_in  : in  camera_in;
        
        output : out camera_output);
end camera_wrapper;

architecture arc of camera_wrapper is
    signal clock_out : std_logic;
    
    signal bitslip : std_logic_vector(4 downto 0) := (others => '0');
    signal deserializer_clock : std_logic;
    signal deserializer_out   : std_logic_vector(24 downto 0);
begin
    CLOCK_OUT_DDR : ODDR2
        generic map (
            DDR_ALIGNMENT => "NONE",
            INIT          => '0',
            SRTYPE        => "SYNC")
        port map (
            Q  => clock_out,
            C0 => clock_camera_over_2,
            C1 => not clock_camera_over_2,
            CE => '1',
            D0 => '1',
            D1 => '0',
            R  => '0',
            S  => '0');
    CLOCK_OUT_OBUF : OBUFDS
        generic map (
            IOSTANDARD => "LVDS_33")
        port map (
            I  => clock_out,
            O  => camera_out.clock_p,
            OB => camera_out.clock_n);
    
    deserializer_clock <= clock_camera_over_5;
    DESERIALIZER : entity work.camera_deserializer port map (
        IO_RESET => reset,
        
        CLK_IN => clock_camera_unbuf,
        CLK_DIV_IN => clock_camera_over_5,
        LOCKED_IN => clock_locked,
        DATA_IN_FROM_PINS_P => camera_in.sync_p & camera_in.data3_p &
            camera_in.data2_p & camera_in.data1_p & camera_in.data0_p,
        DATA_IN_FROM_PINS_N => camera_in.sync_n & camera_in.data3_n &
            camera_in.data2_n & camera_in.data1_n & camera_in.data0_n,
        
        LOCKED_OUT => open,
        DATA_IN_TO_DEVICE => deserializer_out,
        BITSLIP => bitslip,
        
        DEBUG_IN => "00",
        DEBUG_OUT => open);
    
    output.clock <= deserializer_clock;
    process (deserializer_clock, deserializer_out) is
        variable bitslip_countdown : integer range 0 to 1000;
        variable odd : boolean;
        type DataArray is array (0 to 3) of unsigned(9 downto 0);
        variable sync_maybe_inv : unsigned(9 downto 0);
        variable data_maybe_inv : DataArray;
        variable sync : unsigned(9 downto 0);
        variable data : DataArray;
        variable data_valid : boolean;
        variable kernel_pos : integer range 0 to 3;
        type Kernel is array (0 to 7) of unsigned(9 downto 0);
        variable even_kernel : Kernel;
        variable odd_kernel : Kernel;
    begin
        if rising_edge(deserializer_clock) then
            -- fill sync_maybe_inv and data_maybe_inv with deserializer_out
            if odd = false then
                for i in 0 to 4 loop
                    for j in 0 to 3 loop
                        data_maybe_inv(j)(5+i) := deserializer_out(j+5*i);
                    end loop;
                    sync_maybe_inv(5+i) := deserializer_out(4+5*i);
                end loop;
                odd := true;
            else
                for i in 0 to 4 loop
                    for j in 0 to 3 loop
                        data_maybe_inv(j)(i) := deserializer_out(j+5*i);
                    end loop;
                    sync_maybe_inv(i) := deserializer_out(4+5*i);
                end loop;
                odd := false;
            end if;
            
            if odd = true then -- sync_maybe_inv and data_maybe_inv are valid
                -- process sync_maybe_inv and data_maybe_inv into sync and data
                if SYNC_INVERTED then sync := not sync_maybe_inv; else sync := sync_maybe_inv; end if;
                if DATA3_INVERTED then data(3) := not data_maybe_inv(3); else data(3) := data_maybe_inv(3); end if;
                if DATA2_INVERTED then data(2) := not data_maybe_inv(2); else data(2) := data_maybe_inv(2); end if;
                if DATA1_INVERTED then data(1) := not data_maybe_inv(1); else data(1) := data_maybe_inv(1); end if;
                if DATA0_INVERTED then data(0) := not data_maybe_inv(0); else data(0) := data_maybe_inv(0); end if;
            end if;
            
            if bitslip_countdown /= 0 then
                bitslip_countdown := bitslip_countdown - 1;
            end if;
            
            bitslip <= (others => '0');
            output.line_valid <= '0';
            output.pixel1 <= XXX;
            
            if odd = true then -- sync+data are valid
                -- process sync, data
                
                data_valid := false;
                if sync_is_window_id then
                    sync_is_window_id := false;
                    data_valid := true;
                elsif sync = to_unsigned(16#5#, 3) & to_unsigned(16#2A#, 7) then -- frame start
                    data_valid := true;
                    sync_is_window_id := true;
                elsif sync = to_unsigned(16#6#, 3) & to_unsigned(16#2A#, 7) then -- frame end
                    data_valid := true;
                    sync_is_window_id := true;
                elsif sync = to_unsigned(16#1#, 3) & to_unsigned(16#2A#, 7) then -- line start
                    data_valid := true;
                    sync_is_window_id := true;
                    kernel_pos := 0;
                elsif sync = to_unsigned(16#2#, 3) & to_unsigned(16#2A#, 7) then -- line end
                    data_valid := true;
                    sync_is_window_id := true;
                elsif sync = to_unsigned(16#015#, 10) then -- black
                elsif sync = to_unsigned(16#035#, 10) then -- valid
                    data_valid := true;
                elsif sync = to_unsigned(16#059#, 10) then -- CRC
                elsif sync = to_unsigned(16#3A6#, 10) then -- train
                    for i in 0 to 3 loop
                        if data(i) /= to_unsigned(16#3A6#, 10) then
                            if bitslip_countdown /= 0 then
                                bitslip(i) <= '1'; -- slip data
                                bitslip_countdown := 1000;
                            end if;
                        end if;
                    end loop;
                else
                    if bitslip_countdown /= 0 then
                        bitslip(4) <= '1'; -- slip sync
                        bitslip_countdown := 1000;
                    end if;
                end if;
                
                if data_valid then
                    if kernel_pos = 0 then
                        even_kernel(0) := data(0);
                        even_kernel(2) := data(1);
                        even_kernel(4) := data(2);
                        even_kernel(6) := data(3);
                        kernel_pos := 1;
                    elsif kernel_pos = 1 then
                        even_kernel(1) := data(0);
                        even_kernel(3) := data(1);
                        even_kernel(5) := data(2);
                        even_kernel(7) := data(3);
                        kernel_pos := 2;
                    elsif kernel_pos = 2 then
                        odd_kernel (7) := data(0);
                        odd_kernel (5) := data(1);
                        odd_kernel (3) := data(2);
                        odd_kernel (1) := data(3);
                        kernel_pos := 3;
                    elsif kernel_pos = 3 then
                        odd_kernel (6) := data(0);
                        odd_kernel (4) := data(1);
                        odd_kernel (2) := data(2);
                        odd_kernel (0) := data(3);
                        kernel_pos := 0;
                    end if;
                end if;
            end if;
        end if;
    end process;
end architecture;
