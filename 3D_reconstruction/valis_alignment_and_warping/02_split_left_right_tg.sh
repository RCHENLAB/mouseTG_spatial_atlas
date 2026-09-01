#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Cut each section image into its left and right trigeminal ganglion with the drawn polygons.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

for side in "${SIDES[@]}"; do
	mkdir -p "$TGIMAGEDIR/$side"
	sidesections "$side" | while IFS=$'\t' read -r sampleid polygon image; do
		"$PYTHON" "$PYDIR/tiff2maskbypolygon.py" -d "$TGIMAGEDIR/$side" -b "$sampleid" \
			-m "$polygon" --rgb --whitebg "$RGBDIR/$sampleid.tif"
	done
done
