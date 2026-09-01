#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Convert the Cellpose boundaries of each .zarr to .geojson (pixel coordinates).

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$NONNEURONGEOJSONDIR"

find "$NONNEURONSEGDIR" -path '*/cellpose_boundaries/*' -not -path '*/RNA/*' -name shapes.parquet | while read -r infile; do
	zarrdir=$(dirname "$(dirname "$(dirname "$infile")")")
	bname=$(basename "$zarrdir" .zarr)
	"$PYTHON" "$PYDIR/sopashapesparquet2geojson.py" -d "$NONNEURONGEOJSONDIR" -b "$bname" -s 1.0 "$infile"
done
