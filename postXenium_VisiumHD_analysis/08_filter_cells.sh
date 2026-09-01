#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Drop cells and genes without counts after aggregation.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$FILTERDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/scrnah5adfiltergenescellsbycounts.py" -d "$FILTERDIR" -b "$sampleid" \
		-c "$MINCOUNT" -k "$CELLH5ADDIR/$sampleid.h5ad"
done
