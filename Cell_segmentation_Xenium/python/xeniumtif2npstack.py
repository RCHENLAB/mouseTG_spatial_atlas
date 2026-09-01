#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Stack single-channel TIFF files into one multi-channel OME-TIFF.

import argparse
from pathlib import Path
import numpy as np
import tifffile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('infile', nargs='+')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

images=[
	tifffile.imread(file, is_ome=False, level=0)
	for file in infile
	]

ref_shape=images[0].shape
for i, image in enumerate(images[1:]):
	if image.shape!=ref_shape:
		raise ValueError(f"Image {i+1} has mismatched shape: {image.shape} vs {ref_shape}")

images=np.stack(images, axis=0)

tifffile.imwrite(
	f"{outdir}/{bname}.tif",
	images,
	bigtiff=True,
	photometric='minisblack',
	compression='JPEG2000',
	tile=(1024, 1024),
	ome=True,
	)
