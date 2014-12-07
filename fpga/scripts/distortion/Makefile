all: out.hex

out.hex: data.csv data.py
	rm -f dump
	python data.py data.csv

.PHONY: program

program: out.hex write_hex.py
	python write_hex.py out.hex
