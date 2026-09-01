#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Keep the shapes of the cells belonging to one trigeminal ganglion.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

for side in "${SIDES[@]}"; do
	mkdir -p "$SUBSETDIR/$side"
	sidesections "$side" | while IFS=$'\t' read -r sampleid polygon image; do
		subsetfile=$SELECTDIR/$side/$sampleid.txt.gz
		if [ ! -f "$subsetfile" ]; then
			continue
		fi
		for shape in "${SHAPES[@]}"; do
			infile=$SHAPEPIXELDIR/${sampleid}_${shape}.geojson
			if [ ! -f "$infile" ]; then
				continue
			fi
			"$PYTHON" "$PYDIR/geojson2subsetbyproperty.py" -d "$SUBSETDIR/$side" -b "${sampleid}_${shape}" \
				-p cell_id -p index -s "$subsetfile" -f geojson "$infile"
		done
	done
done
