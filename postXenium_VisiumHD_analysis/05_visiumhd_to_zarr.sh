#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Read each Space Ranger bundle into a SpatialData .zarr store.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$ZARRDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/spatialdataiovisiumhd2zarr.py" -d "$ZARRDIR" -b "$sampleid" -a \
		"$COUNTDIR/$sampleid/outs"
done
