library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.video_bus.all;


entity dvi_video_test_pattern_generator is
    port (
        reset  : in  std_logic;
        clk_in : in  std_logic;
        video  : out video_bus);
end dvi_video_test_pattern_generator;

architecture Behavioral of dvi_video_test_pattern_generator is
    signal h_cnt : unsigned(11 downto 0);
    signal v_cnt : unsigned(11 downto 0);
begin

    process(clk_in)
    begin
        if rising_edge(clk_in) then
            if reset = '1' then
                h_cnt <= to_unsigned(H_MAX, h_cnt'length);
                v_cnt <= to_unsigned(V_MAX, v_cnt'length);
            else
                if h_cnt /= H_MAX - 1 then
                    h_cnt <= h_cnt + 1;
                else
                    h_cnt <= to_unsigned(0, h_cnt'length);
                    if v_cnt /= V_MAX - 1 then
                        v_cnt <= v_cnt + 1;
                    else
                        v_cnt <= to_unsigned(0, v_cnt'length);
                    end if;
                end if;
            end if;
        end if;
    end process;

    process(clk_in, reset, h_cnt, v_cnt)
    begin
        video.sync.pixel_clk <= clk_in;
        video.sync.valid <= not reset;
        
        if ((h_cnt / 16) mod 2) = 0 xor ((v_cnt / 16) mod 2) = 0 then
            video.data.red   <= x"FF";
            video.data.green <= x"FF";
            video.data.blue  <= x"FF";
        else
            video.data.red   <= x"00";
            video.data.green <= x"00";
            video.data.blue  <= x"00";
        end if;
        
        video.sync.frame_rst <= '0';
        if h_cnt = H_MAX - 1 and v_cnt = V_MAX - 1 then
            video.sync.frame_rst <= '1';
        end if;
    end process;

end Behavioral;

