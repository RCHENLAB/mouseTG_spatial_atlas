#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Pseudo-colour and invert the stacked Xenium morphology channels, giving one brightfield-like
# RGB image per section for the registration.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$RGBDIR"

samples | while IFS=$'\t' read -r sampleid xeniumstack xeniumdir; do
	"$PYTHON" "$PYDIR/tiffchannel2rgb.py" -d "$RGBDIR" -b "$sampleid" -n "$xeniumstack"
done
