#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Read each re-quantified Xenium bundle into a SpatialData .zarr store.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$ZARRDIR"

samples | while IFS=$'\t' read -r sampleid xeniumstack xeniumdir; do
	"$PYTHON" "$PYDIR/spatialdataioxenium2zarr.py" -d "$ZARRDIR" -b "$sampleid" -c \
		-t "$NUMTHREADS" "$xeniumdir"
done
