all: out.hex

data.csv: data.csv.bz2
	bzcat data.csv.bz2 > data.csv

out.hex: data.csv data.py
	rm -f dump
	python data.py data.csv

.PHONY: program

program: out.hex write_hex.py
	python write_hex.py out.hex
