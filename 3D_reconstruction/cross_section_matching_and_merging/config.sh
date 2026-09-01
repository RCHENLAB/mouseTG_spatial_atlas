#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Shared paths and parameters for cross-section cell matching and merging.
# This module reconstructs 3D cells by matching the SAME cell across adjacent
# serial sections and merging the matched fragments into multi-section chains.

set -euo pipefail

BASEDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PYDIR=$BASEDIR/python
OUTDIR=${OUTDIR:-$BASEDIR/result}

PYTHON=${PYTHON:-python3}
NEURONTYPEFILE=${NEURONTYPEFILE:-$BASEDIR/neuron_types.txt}

SIDES=(left right)

# Input: the per-side all-cell 3D objects from the upstream module
# `3D_reconstruction/valis_alignment_and_warping` (its step 17,
# result/17_h5ad_allcells/mouse_${side}TG_warped_allcells.h5ad).
# Not committed; point WARPEDDIR at those files (or drop/symlink them into input/).
WARPEDDIR=${WARPEDDIR:-$BASEDIR/input}

# --- matching / merging parameters ---
RADIUS=${RADIUS:-30}          # neighbour search radius (microns) for MBN matching
TPSTHRESH=${TPSTHRESH:-50}    # max distance (microns) of a warped source to an anchor
DISTFILTER=${DISTFILTER:-20}  # max accepted link distance (microns) after TPS
MAXSECTIONS=${MAXSECTIONS:-3} # max number of sections a merged cell may span
MINNEURONS=${MINNEURONS:-100} # a section joins the matching block only above this
TPSSMOOTH=${TPSSMOOTH:-0.1}   # thin-plate-spline smoothing

# Output stage directories
EDGEDIR=$OUTDIR/01_match_edges     # candidate same-cell links between sections
CHAINDIR=$OUTDIR/02_merge_chains   # DP-selected multi-section chains
MERGEDIR=$OUTDIR/03_h5ad_merged    # final merged 3D objects

warpedh5ad() { echo "$WARPEDDIR/mouse_${1}TG_warped_allcells.h5ad"; }
