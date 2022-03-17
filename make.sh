#!/bin/bash

for cpu in 6809 6309; do
	srcvhd="/media/share1/EMU/EOU/${cpu:0:2}SDC.VHD"
	for emu in mame xroar; do
		python3 ./makebootfileide.py -c "${cpu}" -i "${srcvhd}" -e "${emu}" -d becker
	done
done
