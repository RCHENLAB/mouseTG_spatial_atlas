#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Aggregate the 2 µm bins into the Xenium cell polygons, keyed by the Xenium cell id.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$CELLH5ADDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/visiumhdh5adsegpolygon2aggregateh5ad.py" -d "$CELLH5ADDIR" -b "$sampleid" \
		-s "$SCALEDIR/$sampleid.geojson" -i "$IDKEY" \
		"$BINH5ADDIR/${sampleid}_${BIN}.h5ad"
done
