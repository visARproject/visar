all: out.hex

data.csv: data.csv.bz2
	time bzcat data.csv.bz2 > data.csv

dump: make_dump.py data.csv calibration.yaml constants.py
	time python make_dump.py data.csv calibration.yaml dump

out.hex: data.py dump constants.py
	time python data.py dump out.hex

.PHONY: program

program: out.hex write_hex.py
	time python write_hex.py out.hex
