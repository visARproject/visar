library ieee;
use ieee.std_logic_1164.all;

package ram_port is
    constant MASK_SIZE           : integer := 4;
    constant DATA_PORT_SIZE      : integer := 32;
    
    subtype Command is std_logic_vector(2 downto 0);
    constant WRITE_COMMAND           : Command := "000";
    constant READ_COMMAND            : Command := "001";
    constant WRITE_PRECHARGE_COMMAND : Command := "010";
    constant READ_PRECHARGE_COMMAND  : Command := "011";
    constant REFRESH                 : Command := "1XX";
    
    
    type ram_port_cmd_in is record
        clk       : std_logic;
        en        : std_logic;
        instr     : std_logic_vector(2 downto 0);
        bl        : std_logic_vector(5 downto 0);
        byte_addr : std_logic_vector(29 downto 0);
    end record;
    type ram_port_cmd_out is record
        empty : std_logic;
        full  : std_logic;
    end record;
    
    type ram_port_wr_in is record
        clk      : std_logic;
        en       : std_logic;
        mask     : std_logic_vector(MASK_SIZE - 1 downto 0);
        data     : std_logic_vector(DATA_PORT_SIZE - 1 downto 0);
    end record;
    type ram_port_wr_out is record
        full     : std_logic;
        empty    : std_logic;
        count    : std_logic_vector(6 downto 0);
        underrun : std_logic;
        error    : std_logic;
    end record;
    
    type ram_port_rd_in is record
        clk : std_logic;
        en  : std_logic;
    end record;
    type ram_port_rd_out is record
        data     : std_logic_vector(DATA_PORT_SIZE - 1 downto 0);
        full     : std_logic;
        empty    : std_logic;
        count    : std_logic_vector(6 downto 0);
        overflow : std_logic;
        error    : std_logic;
    end record;
    
    type ram_bidir_port_in is record
        cmd : ram_port_cmd_in;
        wr : ram_port_wr_in;
        rd: ram_port_rd_in;
    end record;
    type ram_bidir_port_out is record
        cmd : ram_port_cmd_out;
        wr : ram_port_wr_out;
        rd: ram_port_rd_out;
    end record;
    
    type ram_wr_port_in is record
        cmd : ram_port_cmd_in;
        wr : ram_port_wr_in;
    end record;
    type ram_wr_port_out is record
        cmd : ram_port_cmd_out;
        wr : ram_port_wr_out;
    end record;
    
    type ram_rd_port_in is record
        cmd : ram_port_cmd_in;
        rd: ram_port_rd_in;
    end record;
    type ram_rd_port_out is record
        cmd : ram_port_cmd_out;
        rd: ram_port_rd_out;
    end record;

end ram_port;

package body ram_port is

end ram_port;
