#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Match the same neuron across adjacent serial sections, giving candidate
# same-cell links (edges) per side.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$EDGEDIR"

for side in "${SIDES[@]}"; do
	"$PYTHON" "$PYDIR/match_sections.py" \
		-i "$(warpedh5ad "$side")" \
		-o "$EDGEDIR/mouse_${side}TG_match_edges.tsv.gz" \
		--neuron-types "$NEURONTYPEFILE" \
		--radius "$RADIUS" --tps-thresh "$TPSTHRESH" --dist-filter "$DISTFILTER" \
		--min-neurons "$MINNEURONS" --tps-smooth "$TPSSMOOTH"
done
