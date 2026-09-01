#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Turn the candidate links into merged multi-section chains: per cell type, pick a
# non-overlapping set of at most (MAXSECTIONS-1) consecutive links by dynamic
# programming, then take connected components as the chains.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$CHAINDIR"

for side in "${SIDES[@]}"; do
	"$PYTHON" "$PYDIR/merge_chains.py" \
		-e "$EDGEDIR/mouse_${side}TG_match_edges.tsv.gz" \
		-o "$CHAINDIR/mouse_${side}TG_chains.tsv.gz" \
		--radius "$RADIUS" --max-sections "$MAXSECTIONS"
done
