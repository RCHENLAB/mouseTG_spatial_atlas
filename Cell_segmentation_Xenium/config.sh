#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Shared paths and parameters for the Xenium 2D cell segmentation pipeline.

set -euo pipefail

BASEDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SAMPLESHEET=${SAMPLESHEET:-$BASEDIR/samples.tsv}
MARKERSHEET=${MARKERSHEET:-$BASEDIR/markers.tsv}
YAMLDIR=$BASEDIR/yaml
PYDIR=$BASEDIR/python
OUTDIR=${OUTDIR:-$BASEDIR/result}

PYTHON=${PYTHON:-python3}
NUMTHREADS=${NUMTHREADS:-8}
# workflow/ directory of a Sopa checkout: git clone https://github.com/gustaveroussy/sopa
SOPA_WORKFLOW=${SOPA_WORKFLOW:-/path/to/sopa/workflow}
# sourceme.bash shipped with the Xenium Ranger 3.1.0 installation
XENIUMRANGER_CONFIG=${XENIUMRANGER_CONFIG:-/path/to/xeniumranger-3.1.0/xeniumranger-xenium3.1/sourceme.bash}
XENIUMRANGER_LOCALCORES=${XENIUMRANGER_LOCALCORES:-16}
XENIUMRANGER_LOCALMEM=${XENIUMRANGER_LOCALMEM:-64}

STACKDIR=$OUTDIR/01_stack
HISTDIR=$OUTDIR/02_intensity_hist
FILTERDIR=$OUTDIR/03_filter
TRANSCRIPTDIR=$OUTDIR/04_marker_transcript
ISLANDDIR=$OUTDIR/05_neuron_island
MASKDIR=$OUTDIR/06_neuron_masked_tif
NEURONSEGDIR=$OUTDIR/07_neuron_cellpose
NEURONGEOJSONDIR=$OUTDIR/08_neuron_geojson
NONNEURONSEGDIR=$OUTDIR/09_nonneuron_cellpose
NONNEURONGEOJSONDIR=$OUTDIR/10_nonneuron_geojson
NONNEURONSUBSETDIR=$OUTDIR/11_nonneuron_transcript_ratio
COMBINEDIR=$OUTDIR/12_combined_geojson
IMPORTDIR=$OUTDIR/13_xeniumranger_import

# Channel index in the stacked morphology_focus image
CH_DAPI=0
CH_CB=1
CH_RNA=2
CH_PROTEIN=3

# Intensity threshold per channel: DAPI, CB, RNA, Protein
INTENSITY=(200 1000 2000 500)

# Segmentation configurations used for the final cell boundaries
NEURON_SEG=protein_rna_180_t0
NONNEURON_SEG=protein_dapi_20_tm2

# Transcript sets used to filter non-neuron polygons
NEURON_MARKER=neuron3
NONNEURON_MARKER=glianonneuron12
NONNEURON_RATIO=0.1

PIXELSIZE=0.2125

samples() {
	grep -v '^#' "$SAMPLESHEET" | sed 1d | awk -F'\t' 'NF>=2'
}

markers() {
	grep -v '^#' "$MARKERSHEET" | sed 1d | awk -F'\t' 'NF>=2'
}
