#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Re-quantify each Xenium bundle with the custom segmentation (Xenium Ranger 3.1.0, no nuclei expansion).

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$IMPORTDIR"

samples | while IFS=$'\t' read -r sampleid xeniumdir; do
	if [ -d "$IMPORTDIR/$sampleid/outs" ]; then
		continue
	fi
	workdir=$IMPORTDIR/${sampleid}_work
	rm -rf "$workdir"
	mkdir -p "$workdir"
	(
	set +u
	source "$XENIUMRANGER_CONFIG"
	set -u
	cd "$workdir"
	xeniumranger import-segmentation \
		--id "$sampleid" \
		--xenium-bundle "$xeniumdir" \
		--nuclei "$NONNEURONGEOJSONDIR/${sampleid}_${NONNEURON_SEG}.geojson" \
		--expansion-distance 0 \
		--cells "$COMBINEDIR/${sampleid}.geojson" \
		--units pixels \
		--jobmode local \
		--localcores "$XENIUMRANGER_LOCALCORES" \
		--localmem "$XENIUMRANGER_LOCALMEM" \
		--disable-ui true
	)
	mkdir -p "$IMPORTDIR/$sampleid"
	mv "$workdir/$sampleid/outs" "$IMPORTDIR/$sampleid/outs"
	rm -rf "$workdir"
done
