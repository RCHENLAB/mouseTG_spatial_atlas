#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Carry the cell type annotation of each cell onto its warped shape.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
shopt -s nullglob

for side in "${SIDES[@]}"; do
	mkdir -p "$ANNOTDIR/$side"
	for infile in "$WARPDIR/$side"/*.geojson; do
		bname=$(basename "$infile" .geojson)
		sampleid=$bname
		for shape in "${SHAPES[@]}"; do
			sampleid=${sampleid%_$shape}
		done
		"$PYTHON" "$PYDIR/geojson2addpropertyby.py" -d "$ANNOTDIR/$side" -b "$bname" \
			-k cell_id -k index -m "$SELECTDIR/$side/${sampleid}_metadata.txt.gz" \
			-K cell_id -v final_annot "$infile"
	done
done
