#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Invert the aligned images back to a dark background, for figures and visual inspection.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
shopt -s nullglob

for side in "${SIDES[@]}"; do
	bname=$(alignname "$side")
	mkdir -p "$INVERTDIR/$side"
	for infile in "$ALIGNDIR/${bname}_align"/*.ome.tiff; do
		"$PYTHON" "$PYDIR/tiffcolor2invertintensity.py" -d "$INVERTDIR/$side" \
			-b "$(basename "$infile" .ome.tiff)" --rgb "$infile"
	done
done
