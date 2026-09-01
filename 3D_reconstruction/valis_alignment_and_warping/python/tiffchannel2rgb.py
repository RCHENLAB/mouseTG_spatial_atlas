#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Blend the channels of a multi-channel TIFF into one pseudo-coloured RGB image, optionally inverted
# so that the dark-background fluorescence image reads as a brightfield image.

import argparse
from pathlib import Path
import numpy as np
import tifffile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-n', '--invert', action='store_true', help='Invert intensity.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
invert=args.invert
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

def normalize(img):
	img=img.astype(np.float32)
	return (img - img.min()) / (img.max() - img.min() + 1e-8)

def blend_channels(image):
	n_channels, img_height, img_width=image.shape

	# Default pseudocolors for up to 10 channels
	DEFAULT_COLORS=[
		[0.0, 1.0, 1.0], # cyan
		[1.0, 1.0, 0.0], # yellow
		[1.0, 0.0, 1.0], # magenta
		[1.0, 0.0, 0.0], # red
		[1.0, 0.5, 0.0], # orange
		[0.6, 0.0, 0.6], # purple
		[0.0, 1.0, 0.0], # green
		[0.3, 1.0, 0.3], # light green
		[0.0, 0.0, 1.0], # blue
		[0.5, 0.5, 0.5], # gray
	]
	channel_colors=DEFAULT_COLORS[:n_channels]

	rgb_image=np.zeros((img_height, img_width, 3), dtype=np.float32)

	for channel_idx in range(n_channels):
		norm_channel=normalize(image[channel_idx])
		rgb_image += np.expand_dims(norm_channel, axis=-1) * channel_colors[channel_idx]

	rgb_image=np.clip(rgb_image, 0, 1)
	return rgb_image

image=tifffile.imread(infile, is_ome=False, level=0)
rgb=blend_channels(image)

rgb_8bit=(rgb*np.iinfo(np.uint8).max).round().astype(np.uint8)

if invert:
	rgb_8bit=np.iinfo(np.uint8).max-rgb_8bit

tifffile.imwrite(f"{outdir}/{bname}.tif", rgb_8bit, compression='zlib', photometric='rgb')
