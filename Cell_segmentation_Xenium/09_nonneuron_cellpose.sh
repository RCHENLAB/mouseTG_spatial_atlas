#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Cellpose (cyto3) non-neuron nuclei segmentation on the filtered image, run through the Sopa Snakemake workflow.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
mkdir -p "$NONNEURONSEGDIR"
cp -r "$SOPA_WORKFLOW"/. "$NONNEURONSEGDIR"/

samples | while IFS=$'\t' read -r sampleid _; do
	for config in "$YAMLDIR"/nonneuron/*.yaml; do
		bname=${sampleid}_$(basename "$config" .yaml)
		(
		cd "$NONNEURONSEGDIR"
		snakemake --configfile "$config" \
			--config data_path="$FILTERDIR/$sampleid.tif" sdata_path="$NONNEURONSEGDIR/$bname.zarr" \
			--directory "$NONNEURONSEGDIR" --cores "$NUMTHREADS" --jobs "$NUMTHREADS" --printshellcmds
		)
	done
done
