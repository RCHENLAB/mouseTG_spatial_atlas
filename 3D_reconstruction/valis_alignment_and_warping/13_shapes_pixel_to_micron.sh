#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Convert the warped coordinates from aligned image pixels back to microns.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
shopt -s nullglob

for side in "${SIDES[@]}"; do
	mkdir -p "$MICRONDIR/$side"
	for infile in "$ANNOTDIR/$side"/*.geojson; do
		bname=$(basename "$infile" .geojson)
		"$PYTHON" "$PYDIR/geojson2xyscale.py" -d "$MICRONDIR/$side" -b "$bname" \
			-x "$PIXELSIZE" -y "$PIXELSIZE" "$infile"
	done
done
