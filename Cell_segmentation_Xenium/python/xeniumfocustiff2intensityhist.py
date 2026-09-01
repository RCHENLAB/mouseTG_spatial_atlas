#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Histogram of pixel intensities for one channel of a Xenium staining TIFF.

import argparse
from pathlib import Path
import numpy as np
import tifffile
from matplotlib import pyplot as plt

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname')
parser.add_argument('-B', '--breaks', type=int, default=1000)
parser.add_argument('-m', '--minintensity', type=int, default=0)
parser.add_argument('-W', '--width', type=float, default=5)
parser.add_argument('-H', '--height', type=float, default=5)
parser.add_argument('-s', '--scale', action='store_true', help='Scale intensities to uint8.')
parser.add_argument('-T', '--transform', action='store_true', help='log10 transform intensities.')
parser.add_argument('-c', '--channel', type=int, default=0)
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname if args.bname else Path(args.infile).stem
breaks=args.breaks
minintensity=args.minintensity
width=args.width
height=args.height
scale=args.scale
transform=args.transform
channel=args.channel
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

image=tifffile.imread(infile, is_ome=False, level=0)
print(f"==> {image.shape}")
print(f"==> {image.dtype}")

if image.ndim==3: # use one channel only
	if image.shape[2]==3: # an RGB image
		image=image[:, :, channel]
	else:
		image=image[channel, :, :]

intensity=image.flatten()
print(f"==> {intensity.shape}")
print(f"==> {intensity.dtype}")

if minintensity>0:
	intensity=intensity[intensity>minintensity]

if scale:
	intensity=np.array((intensity*1.0/intensity.max())*255, dtype=np.uint8)

if transform:
	intensity=np.log10(intensity+1e-6)

plt.figure(figsize=(width, height), dpi=50)
plt.hist(intensity, bins=breaks)
plt.xlabel(f"{'log10(Intensity)' if transform else 'Intensity'}")
plt.ylabel("Frequency")
plt.savefig(f"{outdir}/{bname}.pdf", bbox_inches='tight')
plt.close()
