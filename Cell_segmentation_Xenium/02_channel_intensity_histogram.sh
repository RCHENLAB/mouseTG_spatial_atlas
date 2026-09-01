#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Per-channel intensity histograms used to choose the background thresholds in 03.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$HISTDIR"

samples | while IFS=$'\t' read -r sampleid _; do
	for chnidx in "$CH_DAPI" "$CH_CB" "$CH_RNA" "$CH_PROTEIN"; do
		"$PYTHON" "$PYDIR/xeniumfocustiff2intensityhist.py" -d "$HISTDIR" -b "${sampleid}_${chnidx}" \
			-m 1 -T -B 1000 -W 4 -H 4 -c "$chnidx" "$STACKDIR/$sampleid.tif"
	done
done
