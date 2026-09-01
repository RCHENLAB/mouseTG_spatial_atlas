#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Invert the intensities of an image.

import argparse
from pathlib import Path
import numpy as np
import tifffile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-r', '--rgb', action='store_true', help='Save as RGB.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
rgb=args.rgb
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

image=tifffile.imread(infile, is_ome=False, level=0)
print(f"==> {image.shape=}, {image.dtype=}", flush=True)

invert_image=np.iinfo(image.dtype).max-image
print(f"==> invert, {invert_image.shape=}, {invert_image.dtype=}", flush=True)

tifffile.imwrite(
	f"{outdir}/{bname}.tif",
	invert_image,
	photometric='rgb' if rgb else 'minisblack',
	compression='lzw',
	bigtiff=False,
	ome=False,
	)
