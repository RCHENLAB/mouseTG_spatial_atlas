#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Stack the four morphology_focus channels (DAPI, CB, RNA, Protein) into one OME-TIFF per section.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$STACKDIR"

samples | while IFS=$'\t' read -r sampleid xeniumdir; do
	"$PYTHON" "$PYDIR/xeniumtif2npstack.py" -d "$STACKDIR" -b "$sampleid" \
		"$xeniumdir"/morphology_focus/morphology_focus_{0000..0003}.ome.tif
done
