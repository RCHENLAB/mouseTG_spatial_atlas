#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Rescale the shapes from microns to image pixels, the space the registration works in.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$SHAPEPIXELDIR"

samples | while IFS=$'\t' read -r sampleid xeniumstack xeniumdir; do
	for shape in "${SHAPES[@]}"; do
		infile=$SHAPEDIR/${sampleid}_${shape}.geojson
		if [ ! -f "$infile" ]; then
			continue
		fi
		"$PYTHON" "$PYDIR/geojson2xyscale.py" -d "$SHAPEPIXELDIR" -b "${sampleid}_${shape}" \
			-x "$MICRON2PIXEL" -y "$MICRON2PIXEL" "$infile"
	done
done
