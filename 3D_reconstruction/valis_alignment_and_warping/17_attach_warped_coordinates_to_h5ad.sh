#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Attach the warped coordinates to the expression matrix, giving the all-cell 3D object per side.
# The merge is inner, so each object holds the cells of that ganglion that carry warped coordinates.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$ALLCELLDIR"

for side in "${SIDES[@]}"; do
	metavalue=(-v warp_x -v warp_y -v warp_z)
	if [ -f "$NEIGHBORDIR/mouseTG_${side}_${POINTSHAPE}.parquet" ]; then
		metavalue+=(-v neighborhood)
	fi
	"$PYTHON" "$PYDIR/h5adaddmetadatamergebycompositekey.py" -d "$ALLCELLDIR" -b "mouse_${side}TG_warped_allcells" \
		-m "$COORDDIR/mouseTG_${side}_${POINTSHAPE}.txt.gz" \
		-l sampleid -l cell_id -r slicename -r cell_id \
		"${metavalue[@]}" -t inner -N Unassigned \
		"$EXPRH5AD"
done
