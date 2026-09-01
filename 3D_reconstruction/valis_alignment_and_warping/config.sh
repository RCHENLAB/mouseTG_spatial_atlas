#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Shared paths and parameters for the serial section alignment and coordinate warping.

set -euo pipefail

BASEDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SAMPLESHEET=${SAMPLESHEET:-$BASEDIR/samples.tsv}
SIDESHEET=${SIDESHEET:-$BASEDIR/sides.tsv}
NEURONTYPEFILE=${NEURONTYPEFILE:-$BASEDIR/neuron_types.txt}
PYDIR=$BASEDIR/python
OUTDIR=${OUTDIR:-$BASEDIR/result}

PYTHON=${PYTHON:-python3}
NUMTHREADS=${NUMTHREADS:-8}

# Per-cell annotation table: sampleid, cell_id, x, y (microns) and final_annot
CELLMETA=${CELLMETA:-$BASEDIR/metadata/mouseTG_metadata.txt.gz}
# Concatenated Xenium expression matrix of all sections, obs keyed by sampleid and cell_id
EXPRH5AD=${EXPRH5AD:-$BASEDIR/metadata/mouseTG_expr.h5ad}
# Optional niche/neighborhood table: sampleid, cell_id, neighborhood
NEIGHBORHOOD=${NEIGHBORHOOD:-$BASEDIR/metadata/mouseTG_neighborhood.txt.gz}

SIDES=(left right)

# Xenium image pixel size, and its reciprocal
PIXELSIZE=0.2125
MICRON2PIXEL=4.70588235294117647058

# Serial section spacing along z, in microns
ZSTART=0
ZSTEP=12

# Shapes warped for each section; the 3D point cloud is built from POINTSHAPE
SHAPES=(cell_circles cell_boundaries nucleus_boundaries)
POINTSHAPE=cell_circles

# Valis registration
VALIS_CROP=overlap
VALIS_MAXPROCESSDIM=1024
VALIS_MAXNONRIGIDDIM=1024

RGBDIR=$OUTDIR/01_section_rgb
TGIMAGEDIR=$OUTDIR/02_tg_image
ALIGNDIR=$OUTDIR/03_valis_align
INVERTDIR=$OUTDIR/04_aligned_inverted
TGLABELDIR=$OUTDIR/05_tglabel
ZARRDIR=$OUTDIR/06_zarr
SHAPEDIR=$OUTDIR/07_shapes_micron
SHAPEPIXELDIR=$OUTDIR/08_shapes_pixel
SELECTDIR=$OUTDIR/09_cellid_by_side
SUBSETDIR=$OUTDIR/10_shapes_by_side
WARPDIR=$OUTDIR/11_shapes_warped
ANNOTDIR=$OUTDIR/12_shapes_annotated
MICRONDIR=$OUTDIR/13_shapes_warped_micron
POINTDIR=$OUTDIR/14_points_3d
NEIGHBORDIR=$OUTDIR/15_points_neighborhood
COORDDIR=$OUTDIR/16_warped_coordinates
ALLCELLDIR=$OUTDIR/17_h5ad_allcells
NEURONDIR=$OUTDIR/18_h5ad_neuron

samples() {
	grep -v '^#' "$SAMPLESHEET" | sed 1d | awk -F'\t' 'NF>=3'
}

# Sections of one side, in serial order: sampleid, polygon, image mode (mask|whole)
sidesections() {
	grep -v '^#' "$SIDESHEET" | sed 1d | awk -F'\t' -v side="$1" '$1==side && NF>=4 {print $2 "\t" $3 "\t" $4}'
}

# Image handed to Valis for one section of one side
sideimage() {
	local side=$1 sampleid=$2 mode=$3
	if [ "$mode" = whole ]; then
		echo "$RGBDIR/$sampleid.tif"
	else
		echo "$TGIMAGEDIR/$side/$sampleid.tif"
	fi
}

# Valis names the registration after the side and the crop method
alignname() {
	echo "mouseTG_$1_$VALIS_CROP"
}

registrarfile() {
	local bname
	bname=$(alignname "$1")
	echo "$ALIGNDIR/${bname}_work/${bname}/data/${bname}_registrar.pickle"
}
