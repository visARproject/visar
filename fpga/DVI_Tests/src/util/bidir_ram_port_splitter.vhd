library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;

entity util_bidir_ram_port_splitter is
    port (
        clock : std_logic; -- should be faster or as fast as cmd clocks
        reset : std_logic; -- can be asynchronous
        
        ram_in  : out ram_bidir_port_in;
        ram_out : in  ram_bidir_port_out;
        
        ram_rd_in  : in  ram_rd_port_in;
        ram_rd_out : out ram_rd_port_out;
        
        ram_wr_in  : in  ram_wr_port_in;
        ram_wr_out : out ram_wr_port_out);
end entity;

architecture arc of util_bidir_ram_port_splitter is
    signal reset_synchronized : std_logic;
    
    constant COMMAND_WIDTH : natural := ram_port_cmd_in.instr'length + ram_port_cmd_in.bl'length + ram_port_cmd_in.byte_addr'length;
    
    signal rd_cmd_fifo_read_enable, wr_cmd_fifo_read_enable : std_logic;
    signal rd_cmd_fifo_read_data,   wr_cmd_fifo_read_data   : std_logic_vector(COMMAND_WIDTH-1 downto 0);
    signal rd_cmd_fifo_read_empty,  wr_cmd_fifo_read_empty  : std_logic;
begin
    U_RESET_GEN : entity work.reset_gen port map (
        clock     => clock,
        reset_in  => reset,
        reset_out => reset_synchronized);
    
    ram_in.rd <= ram_rd_in.rd;
    ram_rd_out.rd <= ram_out.rd;
    
    ram_in.wr <= ram_wr_in.wr;
    ram_wr_out.wr <= ram_out.wr;
    
    RD_CMD_FIFO : entity work.util_fifo_fallthrough
        generic map (
            WIDTH => COMMAND_WIDTH,
            LOG_2_DEPTH => 4,
            WRITE_WIDTH => COMMAND_WIDTH,
            READ_WIDTH => COMMAND_WIDTH)
        port map (
            write_clock => ram_rd_in.cmd.clk,
            -- write_reset unnecessary since it would have no effect since WIDTH = WRITE_WIDTH
            write_enable => ram_rd_in.cmd.en,
            write_data => ram_rd_in.cmd.instr & ram_rd_in.cmd.bl & ram_rd_in.cmd.byte_addr,
            write_full => ram_rd_out.cmd.full,
            
            read_clock => clock,
            read_reset => reset_synchronized,
            read_enable => rd_cmd_fifo_read_enable,
            read_data => rd_cmd_fifo_read_data,
            read_empty => rd_cmd_fifo_read_empty);
    
    WR_CMD_FIFO : entity work.util_fifo_fallthrough
        generic map (
            WIDTH => COMMAND_WIDTH,
            LOG_2_DEPTH => 4,
            WRITE_WIDTH => COMMAND_WIDTH,
            READ_WIDTH => COMMAND_WIDTH)
        port map (
            write_clock => ram_wr_in.cmd.clk,
            -- write_reset unnecessary since it would have no effect since WIDTH = WRITE_WIDTH
            write_enable => ram_wr_in.cmd.en,
            write_data => ram_wr_in.cmd.instr & ram_wr_in.cmd.bl & ram_wr_in.cmd.byte_addr,
            write_full => ram_wr_out.cmd.full,
            
            read_clock => clock,
            read_reset => reset_synchronized,
            read_enable => wr_cmd_fifo_read_enable,
            read_data => wr_cmd_fifo_read_data,
            read_empty => wr_cmd_fifo_read_empty);
    
    ram_rd_out.cmd.empty <= ram_out.cmd.empty; -- XXX synchronize to ram_rd_in.cmd.clock
    ram_wr_out.cmd.empty <= ram_out.cmd.empty; -- XXX synchronize to ram_wr_in.cmd.clock
    
    ram_in.cmd.clk <= clock;
    
    process (ram_out.cmd.full, rd_cmd_fifo_read_empty, rd_cmd_fifo_read_data, wr_cmd_fifo_read_empty, wr_cmd_fifo_read_data, clock) is
    begin
        rd_cmd_fifo_read_enable <= '0';
        wr_cmd_fifo_read_enable <= '0';
        if ram_out.cmd.full = '0' then
            if rd_cmd_fifo_read_empty = '0' then
                rd_cmd_fifo_read_enable <= '1';
            elsif wr_cmd_fifo_read_empty = '0' then
                wr_cmd_fifo_read_enable <= '1';
            end if;
        end if;
        if rising_edge(clock) then
            ram_in.cmd.en <= '0';
            ram_in.cmd.instr <= (others => '-');
            ram_in.cmd.bl <= (others => '-');
            ram_in.cmd.byte_addr <= (others => '-');
            if ram_out.cmd.full = '0' then
                if rd_cmd_fifo_read_empty = '0' then
                    ram_in.cmd.en <= '1';
                    ram_in.cmd.instr <= rd_cmd_fifo_read_data(COMMAND_WIDTH-1 downto COMMAND_WIDTH-ram_port_cmd_in.instr'length);
                    ram_in.cmd.bl <= rd_cmd_fifo_read_data(COMMAND_WIDTH-ram_port_cmd_in.instr'length-1 downto ram_port_cmd_in.byte_addr'length);
                    ram_in.cmd.byte_addr <= rd_cmd_fifo_read_data(ram_port_cmd_in.byte_addr'length-1 downto 0);
                elsif wr_cmd_fifo_read_empty = '0' then
                    ram_in.cmd.en <= '1';
                    ram_in.cmd.instr <= wr_cmd_fifo_read_data(COMMAND_WIDTH-1 downto COMMAND_WIDTH-ram_port_cmd_in.instr'length);
                    ram_in.cmd.bl <= wr_cmd_fifo_read_data(COMMAND_WIDTH-ram_port_cmd_in.instr'length-1 downto ram_port_cmd_in.byte_addr'length);
                    ram_in.cmd.byte_addr <= wr_cmd_fifo_read_data(ram_port_cmd_in.byte_addr'length-1 downto 0);
                end if;
            end if;
        end if;
    end process;
end architecture;
