#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Warp the shapes of every section from its own image space into the aligned stack.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
shopt -s nullglob

for side in "${SIDES[@]}"; do
	registrar=$(registrarfile "$side")
	mkdir -p "$WARPDIR/$side"
	for infile in "$SUBSETDIR/$side"/*.geojson; do
		bname=$(basename "$infile" .geojson)
		slidename=$bname
		for shape in "${SHAPES[@]}"; do
			slidename=${slidename%_$shape}
		done
		if [ -f "$WARPDIR/$side/$bname.geojson" ]; then
			continue
		fi
		"$PYTHON" "$PYDIR/valisregistrar2warpgeojson.py" -d "$WARPDIR/$side" -b "$bname" \
			-r "$registrar" -s "$slidename" -c "$VALIS_CROP" "$infile"
	done
done
