#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Export marker transcript coordinates per section, used to filter non-neuron polygons in 11.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$TRANSCRIPTDIR"

samples | while IFS=$'\t' read -r sampleid xeniumdir; do
	markers | while IFS=$'\t' read -r name marker; do
		symbolopts=()
		for symbol in ${marker//,/ }; do
			symbolopts+=(-s "$symbol")
		done
		"$PYTHON" "$PYDIR/xeniumtranscriptsparquet2csv.py" -d "$TRANSCRIPTDIR" -b "${sampleid}_${name}" \
			-l 0 "${symbolopts[@]}" "$xeniumdir/transcripts.parquet"
	done
done
