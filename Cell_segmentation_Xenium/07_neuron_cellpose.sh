#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Cellpose (cyto3) neuron segmentation on the island-masked image, run through the Sopa Snakemake workflow.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$NEURONSEGDIR"
cp -r "$SOPA_WORKFLOW"/. "$NEURONSEGDIR"/

samples | while IFS=$'\t' read -r sampleid _; do
	for config in "$YAMLDIR"/neuron/*.yaml; do
		bname=${sampleid}_$(basename "$config" .yaml)
		(
		cd "$NEURONSEGDIR"
		snakemake --configfile "$config" \
			--config data_path="$MASKDIR/$sampleid.tif" sdata_path="$NEURONSEGDIR/$bname.zarr" \
			--directory "$NEURONSEGDIR" --cores "$NUMTHREADS" --jobs "$NUMTHREADS" --printshellcmds
		)
	done
done
