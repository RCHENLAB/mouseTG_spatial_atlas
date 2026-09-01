#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Filter out background pixels channel-wise: DAPI 200, CB 1000, RNA 2000, Protein 500.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$FILTERDIR"

intensityopts=()
for intensity in "${INTENSITY[@]}"; do
	intensityopts+=(-i "$intensity")
done

samples | while IFS=$'\t' read -r sampleid _; do
	"$PYTHON" "$PYDIR/xeniumfocustiff2filterbyintensity.py" -d "$FILTERDIR" -b "$sampleid" \
		"${intensityopts[@]}" "$STACKDIR/$sampleid.tif"
done
