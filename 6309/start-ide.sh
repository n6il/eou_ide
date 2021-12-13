#!/bin/bash
xroar \
	-machine coco3 \
	-machine-cpu 6309 \
	-tv-input rgb \
	-machine-cart ide \
	-cart-rom ./hdblba.rom \
	-load-hd0 63IDE.ide \

# DO NOT REMOVE BLANK LINE ABOVE
