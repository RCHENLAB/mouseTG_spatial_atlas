#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Restrict the filtered image to the island mask before neuron segmentation.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$MASKDIR"

samples | while IFS=$'\t' read -r sampleid _; do
	"$PYTHON" "$PYDIR/xeniumfocustiff2maskbyislandimage.py" -d "$MASKDIR" -b "$sampleid" \
		-m "$ISLANDDIR/${sampleid}_expmask.tif" -s 127 "$FILTERDIR/$sampleid.tif"
done
