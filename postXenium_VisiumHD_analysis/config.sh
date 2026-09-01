#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Shared paths and parameters for the post-Xenium Visium HD pipeline.

set -euo pipefail

BASEDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SAMPLESHEET=${SAMPLESHEET:-$BASEDIR/samples.tsv}
PYDIR=$BASEDIR/python
OUTDIR=${OUTDIR:-$BASEDIR/result}

PYTHON=${PYTHON:-python3}
NUMTHREADS=${NUMTHREADS:-8}

# sourceme.bash shipped with the Space Ranger 4.1.0 installation
SPACERANGER_CONFIG=${SPACERANGER_CONFIG:-/path/to/spaceranger-4.1.0/sourceme.bash}
GENOME=${GENOME:-/path/to/refdata-gex-mm10-2020-A}
# Visium Mouse Transcriptome Probe Set v2.0 (mm10-2020-A), shipped with Space Ranger
PROBESET=${PROBESET:-/path/to/spaceranger-4.1.0/probe_sets/Visium_Mouse_Transcriptome_Probe_Set_v2.0_mm10-2020-A.csv}
SPACERANGER_LOCALCORES=${SPACERANGER_LOCALCORES:-16}
SPACERANGER_LOCALMEM=${SPACERANGER_LOCALMEM:-32}

RGBDIR=$OUTDIR/01_xenium_rgb
BOUNDARYDIR=$OUTDIR/02_cell_boundaries_geojson
SCALEDIR=$OUTDIR/03_cell_boundaries_pixel
COUNTDIR=$OUTDIR/04_spaceranger_count
ZARRDIR=$OUTDIR/05_zarr
BINH5ADDIR=$OUTDIR/06_bin_h5ad
CELLH5ADDIR=$OUTDIR/07_cell_h5ad
FILTERDIR=$OUTDIR/08_cell_h5ad_filtered
METADIR=$OUTDIR/09_cell_h5ad_annotated

# Xenium image pixel size; the segmentation polygons are converted from microns to pixels
PIXELSIZE=0.2125
XYSCALE=4.70588235294117647058

# Bin size aggregated into the Xenium cell polygons
BIN=square_002um
# Additional bin size requested from Space Ranger, on top of 2/8/16 µm
CUSTOMBIN=4
# Barcode centre to segmented cell distance allowed by Space Ranger
EXPANSION=0
# Minimum counts per cell and per gene after aggregation
MINCOUNT=1
# GeoJSON property used as the cell barcode of the aggregated matrix
IDKEY=id

samples() {
	grep -v '^#' "$SAMPLESHEET" | sed 1d | awk -F'\t' 'NF>=5'
}
