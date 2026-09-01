#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Carry the niche assignment of each cell onto the 3D points. Skipped when no table is given.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$NEIGHBORDIR"

if [ ! -f "$NEIGHBORHOOD" ]; then
	echo "skip: $NEIGHBORHOOD not found" >&2
	exit 0
fi

for side in "${SIDES[@]}"; do
	"$PYTHON" "$PYDIR/geojson2addpropertycompositekey.py" -d "$NEIGHBORDIR" -b "mouseTG_${side}_${POINTSHAPE}" \
		-m "$NEIGHBORHOOD" -l slicename -l cell_id -r sampleid -r cell_id \
		-v neighborhood -t left -N Unassigned \
		"$POINTDIR/mouseTG_${side}_${POINTSHAPE}.parquet"
done
