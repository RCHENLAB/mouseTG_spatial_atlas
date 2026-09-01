#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Keep the neuronal cell types, giving the neuron-only 3D object per side.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$NEURONDIR"

typeopts=()
while read -r celltype; do
	[ -n "$celltype" ] || continue
	typeopts+=(-v "$celltype")
done < "$NEURONTYPEFILE"

for side in "${SIDES[@]}"; do
	"$PYTHON" "$PYDIR/scrnah5adsubsetbycelltype.py" -d "$NEURONDIR" -b "mouse_${side}TG_warped_neuron" \
		-l final_annot "${typeopts[@]}" \
		"$ALLCELLDIR/mouse_${side}TG_warped_allcells.h5ad"
done
