.PHONY: all
all: build/bitgen/.built

.PHONY: program
program: build/bitgen/.built
	@rm -fr build/impact
	@mkdir -p build/impact
	cp build/bitgen/main.bit build/impact/
	cp build/bitgen/main.msk build/impact/
	/bin/echo -e 'setMode -bscan\nsetCable -p auto' \
		'\naddDevice -p 1 -file main.bit\nprogram -p 1\nquit' > build/impact/cmd
	cd build/impact && impact -batch cmd

.PHONY: clean
clean:
	rm -fr build


PART = xc6slx45-csg324-3
TOP = toplevel
UCF_FILES = src/atlys.ucf
SRC_FILES = src/toplevel.vhd

src/toplevel.vhd: src/toplevel.py
	cd src && python toplevel.py

# synthesize
build/xst/.built: main.prj src/toplevel.vhd
	@rm -fr build/xst
	@mkdir -p build/xst
	@touch build/xst/.ts
	@mkdir build/xst/tmp
	@cp main.prj build/xst
	@cp -r src build/xst
	cd build/xst && echo \
		run -tmpdir tmp -xsthdpdir work -ifn main.prj -ofn main -ofmt NGC \
		-p $(PART) -top $(TOP) -opt_mode Speed -opt_level 2 \
		-power NO -iuc NO -keep_hierarchy No -netlist_hierarchy As_Optimized \
		-rtlview Yes -glob_opt AllClockNets -read_cores YES \
		-sd {\"ipcore_dir\"  } -write_timing_constraints NO \
		-cross_clock_analysis NO -hierarchy_separator / -bus_delimiter '<>' \
		-case Maintain -slice_utilization_ratio 100 \
		-bram_utilization_ratio 100 -dsp_utilization_ratio 100 -lc Auto \
		-reduce_control_sets Auto -fsm_extract YES -fsm_encoding Auto \
		-safe_implementation No -fsm_style LUT -ram_extract Yes \
		-ram_style Auto -rom_extract Yes -shreg_extract YES -rom_style Auto \
		-auto_bram_packing NO -resource_sharing YES -async_to_sync NO \
		-shreg_min_size 2 -use_dsp48 Auto -iobuf YES -max_fanout 100000 \
		-bufg 16 -register_duplication YES -register_balancing Yes \
		-move_first_stage YES -move_last_stage YES -optimize_primitives NO \
		-use_clock_enable Auto -use_sync_set Auto -use_sync_reset Auto \
		-iob True -equivalent_register_removal YES \
		-slice_utilization_ratio_maxmargin 5 \
		| xst -ofn xst.log
	@mv build/xst/.ts build/xst/.built

# translate
build/ngdbuild/.built: build/xst/.built
	@rm -fr build/ngdbuild
	@mkdir -p build/ngdbuild
	@touch build/ngdbuild/.ts
	cp build/xst/main.ngc build/ngdbuild/
	@cp -r src build/ngdbuild
	cd build/ngdbuild && ngdbuild \
		-intstyle ise -dd _ngo -sd src/ipcore_dir -nt timestamp \
		$(UCF_FILES:%=-uc %) \
		-p $(PART) main.ngc main.ngd
	@mv build/ngdbuild/.ts build/ngdbuild/.built

# map
build/map/.built: build/ngdbuild/.built
	@rm -fr build/map
	@mkdir -p build/map
	@touch build/map/.ts
	cp build/ngdbuild/main.ngd build/map/
	cd build/map && map \
		-intstyle ise -p $(PART) -w -logic_opt off \
		-ol high -xe n -t 1 -xt 0 -register_duplication off -r 4 \
		-global_opt off -mt 2 -ir off -pr b -lc off -power off \
		-o main_map.ncd main.ngd main.pcf
	@mv build/map/.ts build/map/.built

# place & route
build/par/.built: build/map/.built
	@rm -fr build/par
	@mkdir -p build/par
	cp build/map/main_map.ncd build/par/
	cp build/map/main.pcf build/par/
	@touch build/par/.ts
	cd build/par && par \
		-w -intstyle ise -ol high -xe n -mt 2 \
		main_map.ncd main.ncd main.pcf
	@mv build/par/.ts build/par/.built

# generate programming file
build/bitgen/.built: build/par/.built
	@rm -fr build/bitgen
	@mkdir -p build/bitgen
	cp build/par/main.ncd build/bitgen/
	@touch build/bitgen/.ts
	cd build/bitgen && bitgen \
		-intstyle ise -w -m -g Binary:no -g Compress -g CRC:Enable \
		-g Reset_on_err:No -g ConfigRate:2 -g ProgPin:PullUp \
		-g TckPin:PullUp -g TdiPin:PullUp -g TdoPin:PullUp \
		-g TmsPin:PullUp -g UnusedPin:PullDown -g UserID:0xFFFFFFFF \
		-g ExtMasterCclk_en:No -g SPI_buswidth:1 -g TIMER_CFG:0xFFFF \
		-g multipin_wakeup:No -g StartUpClk:CClk -g DONE_cycle:4 -g \
		GTS_cycle:5 -g GWE_cycle:6 -g LCK_cycle:NoWait -g Security:None \
		-g DonePipe:No -g DriveDone:No -g en_sw_gsr:No -g drive_awake:No \
		-g sw_clk:Startupclk -g sw_gwe_cycle:5 -g sw_gts_cycle:4 main.ncd
	@mv build/bitgen/.ts build/bitgen/.built
