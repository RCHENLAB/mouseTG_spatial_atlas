#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Attach the Xenium per-cell annotations to the aggregated Visium HD cells, matched on cell id.
# METADATADIR holds one <sampleid>_metadata.txt.gz per section; see README.md.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
METADATADIR=${METADATADIR:-$BASEDIR/metadata}
mkdir -p "$METADIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	metadata=$METADATADIR/${sampleid}_metadata.txt.gz
	if [ ! -f "$metadata" ]; then
		echo "skip $sampleid: $metadata not found" >&2
		continue
	fi
	"$PYTHON" "$PYDIR/h5adaddmetadatamerge.py" -d "$METADIR" -b "$sampleid" \
		-m "$metadata" -k _index_ -r cell_id -t left -N Unassigned \
		"$FILTERDIR/$sampleid.h5ad"
done
