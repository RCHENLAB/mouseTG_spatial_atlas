#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Read a Xenium bundle into a SpatialData .zarr store.

import argparse
from pathlib import Path
from spatialdata_io import xenium

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-c', '--cells-as-circles', dest='cells_as_circles', action='store_true', help='Also read cells as circles.')
parser.add_argument('-t', '--numthreads', type=int, default=4)
parser.add_argument('infile', help='Xenium output directory.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
Path(outdir).mkdir(parents=True, exist_ok=True)

sdata=xenium(
	path=args.infile,
	cells_boundaries=True,
	nucleus_boundaries=True,
	cells_as_circles=args.cells_as_circles,
	cells_labels=True,
	nucleus_labels=True,
	transcripts=True,
	morphology_focus=True,
	aligned_images=False,
	cells_table=True,
	n_jobs=args.numthreads,
	)

print(f"{sdata=}", flush=True)

# Filter invalid shapes
for key,value in sdata.shapes.items():
	value=value[value['geometry'].is_valid & ~value['geometry'].is_empty]
	del sdata.shapes[key]
	sdata.shapes[key]=value

print(f"filter, {sdata=}", flush=True)

sdata.write(f"{outdir}/{bname}.zarr")
