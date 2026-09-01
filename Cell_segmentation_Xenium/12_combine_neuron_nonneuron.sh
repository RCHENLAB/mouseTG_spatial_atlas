#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Harmonize neuron and non-neuron polygons into one cell boundary set per section.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$COMBINEDIR"

samples | while IFS=$'\t' read -r sampleid _; do
	"$PYTHON" "$PYDIR/xeniumcombinetgsegmentations.py" -d "$COMBINEDIR" -b "$sampleid" \
		-n "$NONNEURONSUBSETDIR/${sampleid}.geojson" \
		"$NEURONGEOJSONDIR/${sampleid}_${NEURON_SEG}.geojson"
done
