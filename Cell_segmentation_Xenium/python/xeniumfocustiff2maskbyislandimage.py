#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Keep only the pixels covered by an island mask image.

import argparse
from pathlib import Path
import numpy as np
import tifffile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname')
parser.add_argument('-m', '--maskfile', required=True)
parser.add_argument('-s', '--threshold', type=int, default=127)
parser.add_argument('-n', '--invert', action='store_true', help='Mask out the island regions instead.')
parser.add_argument('-f', '--flip', choices=['horizon', 'vertical'])
parser.add_argument('-r', '--rotate90', type=int, choices=[1, 2, 3])
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname if args.bname else Path(args.infile).stem
maskfile=args.maskfile
threshold=args.threshold
invert=args.invert
flip=args.flip
rotate90=args.rotate90
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

# image input
image=tifffile.imread(infile, is_ome=False, level=0)
print(f"==> {image.shape=}, {image.dtype=}")

# mask input
mask=tifffile.imread(maskfile, is_ome=False, level=0)
print(f"==> {mask.shape=}, {mask.dtype=}")

if invert:
	image=np.where(mask>threshold, 0, image)
else:
	image=np.where(mask>threshold, image, 0)

# flip
if flip:
	match flip:
		case 'horizon':
			image=np.fliplr(image)
		case 'vertical':
			image=np.flipud(image)

# rotate
if rotate90:
	image=np.rot90(image, k=rotate90)

# save
tifffile.imwrite(
	f"{outdir}/{bname}.tif",
	image,
	bigtiff=True,
	compression='JPEG2000',
	tile=(1024, 1024),
	photometric='minisblack',
	ome=True,
	)
