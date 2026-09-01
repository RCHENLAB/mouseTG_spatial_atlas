#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Space Ranger 4.1.0 count with the Xenium cell boundaries imported as the custom segmentation.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$COUNTDIR"

samples | while IFS=$'\t' read -r sampleid fastqs cytaimage xeniumdir xeniumstack; do
	if [ -d "$COUNTDIR/$sampleid/outs" ]; then
		continue
	fi
	workdir=$COUNTDIR/${sampleid}_work
	rm -rf "$workdir"
	mkdir -p "$workdir/fastq"
	for fastq in ${fastqs//,/ }; do
		ln -s "$fastq" "$workdir/fastq/"
	done
	(
	set +u
	source "$SPACERANGER_CONFIG"
	set -u
	cd "$workdir"
	spaceranger count \
		--id "$sampleid" \
		--cytaimage "$cytaimage" \
		--image "$RGBDIR/$sampleid.tif" \
		--custom-segmentation-file "$SCALEDIR/$sampleid.geojson" \
		--nucleus-expansion-distance-micron "$EXPANSION" \
		--transcriptome "$GENOME" \
		--probe-set "$PROBESET" \
		--fastqs "$workdir/fastq" \
		--create-bam false \
		--jobmode local \
		--localcores "$SPACERANGER_LOCALCORES" \
		--localmem "$SPACERANGER_LOCALMEM" \
		--custom-bin-size "$CUSTOMBIN" \
		--disable-ui
	)
	mkdir -p "$COUNTDIR/$sampleid"
	mv "$workdir/$sampleid/outs" "$COUNTDIR/$sampleid/outs"
	rm -rf "$workdir"
done
