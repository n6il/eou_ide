#!/bin/bash

for cpu in 6809 6309; do
	srcvhd="/media/share1/EMU/EOU/${cpu:0:2}SDC.VHD"
	for emu in mame xroar; do
		python3 ./makebootfileide.py -c "${cpu}" -i "${srcvhd}" -e "${emu}" -d becker
	done
done

cpu="6809"
srcvhd="/media/share1/EMU/EOU/${cpu:0:2}SDC.VHD"
for kw in coco3fpga_dw_becker coco3fpga_sdboot_dw_becker; do
	python3 ./makebootfileide.py -c "${cpu}" -i "${srcvhd}" -e "coco3fpga" -k "${kw}"
done

