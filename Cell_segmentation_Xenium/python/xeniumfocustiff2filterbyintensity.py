#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Filter out low-intensity (background) pixels channel-wise.

import argparse
from pathlib import Path
import numpy as np
import tifffile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname')
parser.add_argument('-i', '--intensity', type=int, action='append', required=True, help='Intensity threshold, once per channel.')
parser.add_argument('-v', '--invert', action='store_true', help='Filter out high intensities instead.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname if args.bname else Path(args.infile).stem
intensity=args.intensity
invert=args.invert
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

image=tifffile.imread(infile, is_ome=False, level=0)
print(f"==> {image.shape}, {image.dtype}", flush=True)

if image.ndim==2:
	intensity=intensity[0]
	print(f"==> intensity: {intensity}", flush=True)
elif image.ndim==3:
	intensity=np.array(intensity, dtype=image.dtype).reshape(-1, 1, 1)
	print(f"==> intensity: {intensity.shape}", flush=True)

if invert:
	image=np.where(image<=intensity, image, np.iinfo(image.dtype).max)
else:
	image=np.where(image>=intensity, image, np.iinfo(image.dtype).min)

print(f"==> after filter: {image.shape}, {image.dtype}", flush=True)

tifffile.imwrite(
	f"{outdir}/{bname}.tif",
	image,
	compression='lzw',
	photometric='minisblack',
	bigtiff=False,
	ome=False,
	)
