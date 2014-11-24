library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram_port.all;
use work.video_bus.all;

entity video_ram_source is
    port (
        sync     : in  video_sync;
        data_out : out video_data;
        
        ram_in  : out ram_rd_port_in;
        ram_out : in  ram_rd_port_out);
end entity;

architecture arc of video_ram_source is
    signal h_cnt : HCountType;
    signal v_cnt : VCountType;
begin
    u_counter : entity work.video_counter port map (
        sync => sync,
        h_cnt => h_cnt,
        v_cnt => v_cnt);
    
    process(sync, h_cnt, v_cnt)
    begin
        ram_in.cmd.clk <= sync.pixel_clk;
        
        ram_in.cmd.en <= '0';
        ram_in.cmd.instr <= (others => '-');
        ram_in.cmd.byte_addr <= (others => '-');
        ram_in.cmd.bl <= (others => '-');
        
        if h_cnt mod 32 = 0 and h_cnt < H_DISPLAY_END and v_cnt < V_DISPLAY_END then
            ram_in.cmd.en <= '1';
            ram_in.cmd.instr <= READ_COMMAND;
            ram_in.cmd.byte_addr <= std_logic_vector(to_unsigned(
                (v_cnt * 2048 + h_cnt + 32) * 4
            , ram_in.cmd.byte_addr'length));
            ram_in.cmd.bl <= std_logic_vector(to_unsigned(32 - 1, ram_in.cmd.bl'length));
        end if;
    end process;
    
    process (sync, ram_out, h_cnt, v_cnt) is
    begin
        data_out.red   <= ram_out.rd.data( 7 downto  0);
        data_out.green <= ram_out.rd.data(15 downto  8);
        data_out.blue  <= ram_out.rd.data(23 downto 16);
        
        ram_in.rd.clk <= sync.pixel_clk;
        
        ram_in.rd.en <= '0';
        if h_cnt >= 32 and v_cnt < V_DISPLAY_END + 1 then -- (try to) read extra to make sure FIFO is emptied
            ram_in.rd.en <= '1';
        end if;
    end process;
end architecture;
