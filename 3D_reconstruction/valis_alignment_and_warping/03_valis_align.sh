#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Register the serial sections of each trigeminal ganglion with Valis, in the order of sides.tsv.
# Writes the aligned images and the registrar used to warp coordinates in step 11.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$ALIGNDIR"

for side in "${SIDES[@]}"; do
	bname=$(alignname "$side")
	files=()
	names=()
	while IFS=$'\t' read -r sampleid polygon image; do
		files+=("$(sideimage "$side" "$sampleid" "$image")")
		names+=(-n "$sampleid")
	done < <(sidesections "$side")

	"$PYTHON" "$PYDIR/tiffrgb2alignbyvalis.py" -d "$ALIGNDIR" -b "$bname" \
		-c "$VALIS_CROP" --maxprocessdim "$VALIS_MAXPROCESSDIM" --maxnonrigiddim "$VALIS_MAXNONRIGIDDIM" \
		"${names[@]}" "${files[@]}"
done
