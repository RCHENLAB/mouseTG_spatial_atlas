#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Detect interior-RNA enriched islands (neuron-rich regions) from the RNA channel.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$ISLANDDIR"

samples | while IFS=$'\t' read -r sampleid _; do
	"$PYTHON" "$PYDIR/xeniumtif2islandgeojsonbycv2.py" -d "$ISLANDDIR" -b "$sampleid" \
		-k 11 -p 5 -c "$CH_RNA" "$FILTERDIR/$sampleid.tif"
done
