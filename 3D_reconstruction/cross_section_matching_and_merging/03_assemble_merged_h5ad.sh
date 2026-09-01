#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Assemble the merged 3D object: each chain becomes one merged neuron (summed
# expression, mean warped coordinates, aggregated metadata); every unmatched cell
# is carried through as a singleton.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$MERGEDIR"

for side in "${SIDES[@]}"; do
	"$PYTHON" "$PYDIR/assemble_merged_h5ad.py" \
		-i "$(warpedh5ad "$side")" \
		-c "$CHAINDIR/mouse_${side}TG_chains.tsv.gz" \
		-o "$MERGEDIR/mouse_${side}TG_allcells_merged.h5ad" \
		--neuron-types "$NEURONTYPEFILE"
done
