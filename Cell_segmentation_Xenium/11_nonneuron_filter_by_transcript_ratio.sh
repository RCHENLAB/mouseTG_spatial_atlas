#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Drop non-neuron polygons whose non-neuron transcript fraction is below 0.1.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$NONNEURONSUBSETDIR"

samples | while IFS=$'\t' read -r sampleid _; do
	"$PYTHON" "$PYDIR/xeniumsubsetpolygonbytranscriptratio.py" -d "$NONNEURONSUBSETDIR" -b "$sampleid" \
		-n "$TRANSCRIPTDIR/${sampleid}_${NONNEURON_MARKER}.csv" \
		-N "$TRANSCRIPTDIR/${sampleid}_${NEURON_MARKER}.csv" \
		-r "$NONNEURON_RATIO" "$NONNEURONGEOJSONDIR/${sampleid}_${NONNEURON_SEG}.geojson"
done
