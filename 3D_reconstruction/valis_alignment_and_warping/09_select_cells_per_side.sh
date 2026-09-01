#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Split the labelled cells by trigeminal ganglion and by section: an id list and a metadata table each.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

for side in "${SIDES[@]}"; do
	mkdir -p "$SELECTDIR/$side"
	"$PYTHON" "$PYDIR/tsvfile2splitpdgroupby.py" -d "$SELECTDIR/$side" \
		-c sampleid -f "tglabel=${side}TG" -i cell_id "$TGLABELDIR/mouseTG.txt.gz"
done
