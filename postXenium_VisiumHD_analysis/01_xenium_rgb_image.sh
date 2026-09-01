#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Blend the stacked Xenium morphology channels into an inverted RGB image, used as the
# brightfield (--image) input of Space Ranger. --darkimage does not register with the CytAssist image.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$RGBDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	"$PYTHON" "$PYDIR/tiffchannel2rgb.py" -d "$RGBDIR" -b "$sampleid" -n "$xeniumstack"
done
