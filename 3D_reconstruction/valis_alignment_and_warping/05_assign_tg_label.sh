#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Label every cell as leftTG or rightTG by the polygon it falls into, using the same polygons
# that split the images in step 02.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$TGLABELDIR"

maskopts=()
for side in "${SIDES[@]}"; do
	while IFS=$'\t' read -r sampleid polygon image; do
		maskopts+=(-m "$polygon" -i "$sampleid" -n "${side}TG")
	done < <(sidesections "$side")
done

"$PYTHON" "$PYDIR/xeniummetadata2addlabelbypolygon.py" -d "$TGLABELDIR" -b mouseTG \
	-c sampleid -l tglabel -u Unassigned -s "$PIXELSIZE" -x x -y y -t "$NUMTHREADS" \
	"${maskopts[@]}" "$CELLMETA"
