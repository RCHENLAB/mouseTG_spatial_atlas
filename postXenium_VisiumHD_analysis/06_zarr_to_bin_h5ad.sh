#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Export the binned count tables of each .zarr store as .h5ad.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$BINH5ADDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/spatialdatazarr2tablesh5ad.py" -d "$BINH5ADDIR" -b "$sampleid" \
		"$ZARRDIR/$sampleid.zarr"
done
