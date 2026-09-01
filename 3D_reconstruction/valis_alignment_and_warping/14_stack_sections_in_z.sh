#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Stack the sections of each side into one 3D point cloud, 12 µm apart along z.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$POINTDIR"

for side in "${SIDES[@]}"; do
	files=()
	ids=()
	while IFS=$'\t' read -r sampleid polygon image; do
		infile=$MICRONDIR/$side/${sampleid}_${POINTSHAPE}.geojson
		if [ ! -f "$infile" ]; then
			continue
		fi
		files+=("$infile")
		ids+=(-i "$sampleid")
	done < <(sidesections "$side")

	"$PYTHON" "$PYDIR/geojson2pointzstitch.py" -d "$POINTDIR" -b "mouseTG_${side}_${POINTSHAPE}" \
		-s "$ZSTART" -p "$ZSTEP" -t "$NUMTHREADS" -N slicename "${ids[@]}" "${files[@]}"
done
