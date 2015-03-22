library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

use work.camera_pkg.all;
use work.ram_port.all;
use work.util_arbiter_pkg.all;

entity camera is
    generic (
        CLOCK_FREQUENCY : real;
        
        CPLD_CONFIG_BASE : natural;
        
        SYNC_INVERTED   : boolean;
        DATA3_INVERTED  : boolean;
        DATA2_INVERTED  : boolean;
        DATA1_INVERTED  : boolean;
        DATA0_INVERTED  : boolean;
        MEMORY_LOCATION : integer); -- needs to be 4-byte aligned
    port (
        clock               : in std_logic;
        clock_camera_unbuf  : in std_logic;
        clock_camera_over_2 : in std_logic;
        clock_camera_over_5 : in std_logic;
        clock_locked        : in std_logic;
        reset               : in std_logic;
        
        camera_out : out camera_out;
        camera_in  : in  camera_in;
        
        MOSI : out std_logic;
        MISO : in  std_logic;
        SCLK : out std_logic;
        nSS  : out std_logic;
        
        cpld_MOSI : out std_logic;
        cpld_MISO : in  std_logic;
        cpld_SCLK : out std_logic;
        cpld_nSS  : out std_logic;
        
        spi_arbiter_in  : out ArbiterUserIn;
        spi_arbiter_out : in  ArbiterUserOut;
        
        ram_in  : out ram_wr_port_in;
        ram_out : in  ram_wr_port_out);
end camera;

architecture arc of camera is
    signal camera_output : camera_output;
    
    signal reset_synchronized : std_logic;
    
    signal cpld_spi_data_in  : std_logic_vector(19 downto 0);
    signal cpld_spi_start    : std_logic;
    signal cpld_spi_busy     : std_logic;
    signal cpld_spi_data_out : std_logic_vector(19 downto 0);
begin
    U_CAMERA_WRAPPER : entity work.camera_wrapper
        generic map (
            SYNC_INVERTED  => SYNC_INVERTED,
            DATA3_INVERTED => DATA3_INVERTED,
            DATA2_INVERTED => DATA2_INVERTED,
            DATA1_INVERTED => DATA1_INVERTED,
            DATA0_INVERTED => DATA0_INVERTED)
        port map (
            clock_camera_unbuf  => clock_camera_unbuf,
            clock_camera_over_2 => clock_camera_over_2,
            clock_camera_over_5 => clock_camera_over_5,
            clock_locked        => clock_locked,
            reset               => reset,
            
            camera_out => camera_out,
            camera_in  => camera_in,
            
            output => camera_output);
    
    U_CAMERA_WRITER : entity work.camera_writer
        generic map (
            BUFFER_ADDRESS => MEMORY_LOCATION)
        port map (
            camera_output => camera_output,
            
            ram_in  => ram_in,
            ram_out => ram_out);
    
    U_RESET_GEN : entity work.reset_gen port map (
        clock     => clock,
        reset_in  => reset,
        reset_out => reset_synchronized);
    
    spi_arbiter_in.clock <= clock;
    
    U_CPLD_SPI : entity work.util_spi_master
        generic map (
            CLOCK_FREQUENCY => CLOCK_FREQUENCY,
            SCLK_FREQUENCY => 1.0E6,
            DATA_BITS => 20)
        port map (
            clock => clock,
            reset => reset_synchronized,
            
            data_in  => cpld_spi_data_in,
            start    => cpld_spi_start,
            busy     => cpld_spi_busy,
            data_out => cpld_spi_data_out,
            
            nSS  => cpld_nSS,
            SCLK => cpld_SCLK,
            MOSI => cpld_MOSI,
            MISO => cpld_MISO);
    
    SCLK <= 'Z';
    
    process (clock) is
        constant MILLISECOND_CYCLES : natural := integer(ceil(1.0E-3 / CLOCK_FREQUENCY));
        variable countdown : integer range 0 to MILLISECOND_CYCLES;
        
        type StateType is (STATE_START, STATE_1, STATE_2, STATE_3, STATE_4, STATE_5);
        variable state : StateType;
        
        variable cpld_data : std_logic_vector(9 downto 0);
        
        type RegisterInitializationType is record
            address : integer range 0 to 2**9-1;
            data    : integer range 0 to 2**16-1;
        end record;
        type RegisterInitializationArrayType is array (natural range <>) of RegisterInitializationType;
        constant initialization_data : RegisterInitializationArrayType := (
            -- V1-SN/SE 10-bit mode without PLL
            
            -- ENABLE CLOCK MANAGEMENT REGISTER UPLOAD − PART 1
            (address =>   2, data => 16#0001#),
            (address =>  32, data => 16#2000#),
            (address =>  20, data => 16#0001#),
            -- ENABLE CLOCK MANAGEMENT REGISTER UPLOAD − PART 2
            (address =>   9, data => 16#0000#),
            (address =>  32, data => 16#2002#),
            (address =>  34, data => 16#0001#),
            -- REQUIRED REGISTER UPLOAD
            (address =>  41, data => 16#085A#),
            (address => 129, data => 16#C001#),
            (address =>  65, data => 16#288B#),
            (address =>  66, data => 16#53C5#),
            (address =>  67, data => 16#0344#),
            (address =>  68, data => 16#0085#),
            (address =>  70, data => 16#4800#),
            (address => 128, data => 16#4710#),
            (address => 197, data => 16#0103#),
            (address => 176, data => 16#00F5#),
            (address => 180, data => 16#00FD#),
            (address => 181, data => 16#0144#),
            (address => 387, data => 16#549F#),
            (address => 388, data => 16#549F#),
            (address => 389, data => 16#5091#),
            (address => 390, data => 16#1011#),
            (address => 391, data => 16#111F#),
            (address => 392, data => 16#1110#),
            (address => 431, data => 16#0356#),
            (address => 432, data => 16#0141#),
            (address => 433, data => 16#214F#),
            (address => 434, data => 16#214A#),
            (address => 435, data => 16#2101#),
            (address => 436, data => 16#0101#),
            (address => 437, data => 16#0B85#),
            (address => 438, data => 16#0381#),
            (address => 439, data => 16#0181#),
            (address => 440, data => 16#218F#),
            (address => 441, data => 16#218A#),
            (address => 442, data => 16#2101#),
            
            (address => 443, data => 16#0100#),
            (address => 447, data => 16#0B55#),
            (address => 448, data => 16#0351#),
            (address => 449, data => 16#0141#),
            (address => 450, data => 16#214F#),
            (address => 451, data => 16#214A#),
            (address => 452, data => 16#2101#),
            (address => 453, data => 16#0101#),
            (address => 454, data => 16#0B85#),
            (address => 455, data => 16#0381#),
            (address => 456, data => 16#0181#),
            (address => 457, data => 16#218F#),
            (address => 458, data => 16#218A#),
            (address => 459, data => 16#2101#),
            (address => 460, data => 16#0100#),
            (address => 469, data => 16#2184#),
            (address => 472, data => 16#1347#),
            (address => 476, data => 16#2144#),
            (address => 480, data => 16#8D04#),
            (address => 481, data => 16#8501#),
            (address => 484, data => 16#CD04#),
            (address => 485, data => 16#C501#),
            (address => 489, data => 16#0BE2#),
            (address => 493, data => 16#2184#),
            (address => 496, data => 16#1347#),
            (address => 500, data => 16#2144#),
            (address => 504, data => 16#8D04#),
            (address => 505, data => 16#8501#),
            (address => 508, data => 16#CD04#),
            (address => 509, data => 16#C501#),
            -- SOFT POWER UP REGISTER UPLOADS FOR MODE DEPENDENT REGISTERS
            (address =>  32, data => 16#2003#),
            (address =>  10, data => 16#0000#),
            (address =>  64, data => 16#0001#),
            (address =>  72, data => 16#0203#),
            (address =>  40, data => 16#0003#),
            (address =>  48, data => 16#0001#),
            (address => 112, data => 16#0007#));
    begin
        if rising_edge(clock) then
            cpld_spi_start <= '0';
            --camera_spi_start <= '0';
            if reset_synchronized = '1' then
                spi_arbiter_in.request <= '0';
                
                state := STATE_START;
                countdown := 0;
            elsif countdown /= 0 then
                countdown := countdown - 1;
            elsif state = STATE_START then
                spi_arbiter_in.request <= '1';
                if spi_arbiter_out.enable = '1' then
                    cpld_spi_data_in <= (others => '0');
                    cpld_spi_start <= '1';
                    state := STATE_1;
                    countdown := 1;
                end if;
            elsif state = STATE_1 then
                if cpld_spi_busy = '0' then
                    cpld_data := cpld_spi_data_out(9 downto 0);
                    cpld_data(CPLD_CONFIG_BASE+3) := '1';
                    cpld_spi_data_in <= "1010011001" & cpld_data;
                    cpld_spi_start <= '1';
                    state := STATE_2;
                    countdown := 1;
                end if;
            elsif state = STATE_2 then
                if cpld_spi_busy = '0' then
                    cpld_data(CPLD_CONFIG_BASE+2) := '1';
                    cpld_spi_data_in <= "1010011001" & cpld_data;
                    cpld_spi_start <= '1';
                    state := STATE_3;
                    countdown := 1;
                end if;
            elsif state = STATE_3 then
                if cpld_spi_busy = '0' then
                    cpld_data(CPLD_CONFIG_BASE+1) := '1';
                    cpld_spi_data_in <= "1010011001" & cpld_data;
                    cpld_spi_start <= '1';
                    state := STATE_4;
                    countdown := 1;
                end if;
            elsif state = STATE_4 then
                if cpld_spi_busy = '0' then
                    cpld_data(CPLD_CONFIG_BASE+0) := '1';
                    cpld_spi_data_in <= "1010011001" & cpld_data;
                    cpld_spi_start <= '1';
                    state := STATE_5;
                    countdown := 1;
                end if;
            elsif state = STATE_5 then
                if cpld_spi_busy = '0' then
                    spi_arbiter_in.request <= '0';
                end if;
            end if;
        end if;
    end process;
end architecture;
