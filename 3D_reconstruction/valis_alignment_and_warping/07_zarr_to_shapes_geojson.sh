#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Export the cell circles, cell boundaries and nucleus boundaries of each section, in microns.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$SHAPEDIR"

samples | while IFS=$'\t' read -r sampleid xeniumstack xeniumdir; do
	"$PYTHON" "$PYDIR/spatialdatazarr2shapesgeojson.py" -d "$SHAPEDIR" -b "$sampleid" \
		"$ZARRDIR/$sampleid.zarr"
done
