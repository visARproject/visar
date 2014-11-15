library IEEE;
use IEEE.STD_LOGIC_1164.all;

package ram_port is

    constant MASK_SIZE           : integer := 4;
    constant DATA_PORT_SIZE      : integer := 32;    
    
    type ram_port_in is record
        cmd_clk       : std_logic;
        cmd_en        : std_logic;
        cmd_instr     : std_logic_vector(2 downto 0);
        cmd_bl        : std_logic_vector(5 downto 0);
        cmd_byte_addr : std_logic_vector(29 downto 0);
        
        wr_clk        : std_logic;
        wr_en         : std_logic;
        wr_mask       : std_logic_vector(MASK_SIZE - 1 downto 0);
        wr_data       : std_logic_vector(DATA_PORT_SIZE - 1 downto 0);
        
        rd_clk        : std_logic;
        rd_en         : std_logic;
    end record;

    type ram_port_out is record
        cmd_empty   : std_logic;
        cmd_full    : std_logic;
        
        wr_full     : std_logic;
        wr_empty    : std_logic;
        wr_count    : std_logic_vector(6 downto 0);
        wr_underrun : std_logic;
        wr_error    : std_logic;
        
        rd_data     : std_logic_vector(DATA_PORT_SIZE - 1 downto 0);
        rd_full     : std_logic;
        rd_empty    : std_logic;
        rd_count    : std_logic_vector(6 downto 0);
        rd_overflow : std_logic;
        rd_error    : std_logic;
    end record;

end ram_port;

package body ram_port is

end ram_port;
