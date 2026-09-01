#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Expand the 3D points into warp_x, warp_y and warp_z columns.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$COORDDIR"

for side in "${SIDES[@]}"; do
	bname=mouseTG_${side}_${POINTSHAPE}
	infile=$NEIGHBORDIR/$bname.parquet
	if [ ! -f "$infile" ]; then
		infile=$POINTDIR/$bname.parquet
	fi
	"$PYTHON" "$PYDIR/geojsonpointexpand2pdcolumn.py" -d "$COORDDIR" -b "$bname" -p warp_ "$infile"
done
