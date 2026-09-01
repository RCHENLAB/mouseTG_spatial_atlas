#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Convert the Xenium cell boundaries of the imported segmentation to GeoJSON (microns).

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$BOUNDARYDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/xeniumcellboundaries2geojson.py" -d "$BOUNDARYDIR" -b "$sampleid" \
		"$xeniumdir/cell_boundaries.parquet"
done
