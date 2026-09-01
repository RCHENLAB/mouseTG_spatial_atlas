#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Read a Space Ranger Visium HD output bundle into a SpatialData .zarr store.

import argparse
from pathlib import Path
from spatialdata_io import visium_hd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-i', '--dataset-id', dest='dataset_id')
parser.add_argument('-s', '--bin-size', dest='bin_size', type=int, action='append', help='Bin size to load, repeatable. Default: all.')
parser.add_argument('-r', '--raw-counts-file', dest='raw_counts_file', action='store_true', help='Use raw_feature_bc_matrix.h5 instead of filtered_feature_bc_matrix.h5.')
parser.add_argument('-c', '--bins-as-circles', dest='bins_as_circles', action='store_true', help='Represent bins as circles instead of squares.')
parser.add_argument('-F', '--fullres-image-file', dest='fullres_image_file')
parser.add_argument('-a', '--load-all-images', dest='load_all_images', action='store_true')
parser.add_argument('-l', '--annotate-table-by-labels', dest='annotate_table_by_labels', action='store_true')
parser.add_argument('-N', '--skip-nucleus-segmentations', dest='skip_nucleus_segmentations', action='store_true')
parser.add_argument('infile', help='Space Ranger output directory.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
Path(outdir).mkdir(parents=True, exist_ok=True)

sdata=visium_hd(
	path=args.infile,
	dataset_id=args.dataset_id,
	filtered_counts_file=not args.raw_counts_file,
	bin_size=args.bin_size,
	bins_as_squares=not args.bins_as_circles,
	fullres_image_file=args.fullres_image_file,
	load_all_images=args.load_all_images,
	annotate_table_by_labels=args.annotate_table_by_labels,
	load_nucleus_segmentations=not args.skip_nucleus_segmentations, # load nuclei segmentaion if present
	)

print(f"{sdata=}", flush=True)
sdata.write(f"{outdir}/{bname}.zarr")
