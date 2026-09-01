#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Rescale the cell boundaries from microns to Xenium image pixels (1/0.2125 µm per pixel).

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$SCALEDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/geojson2xyscale.py" -d "$SCALEDIR" -b "$sampleid" \
		-x "$XYSCALE" -y "$XYSCALE" "$BOUNDARYDIR/$sampleid.geojson"
done
