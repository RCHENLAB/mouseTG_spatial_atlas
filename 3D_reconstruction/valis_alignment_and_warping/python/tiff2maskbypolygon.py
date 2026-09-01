#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Keep only the part of an image that falls inside a polygon, e.g. one trigeminal ganglion of a section.

import argparse
from pathlib import Path
import numpy as np
import tifffile
import geopandas as gpd
from rasterio.io import MemoryFile
from rasterio.mask import mask as mask_tool

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-m', '--maskfile', required=True, help='Mask .parquet or .geojson file.')
parser.add_argument('-n', '--invert', action='store_true', help='Mask out the polygon instead.')
parser.add_argument('-r', '--rgb', action='store_true', help='Save as RGB.')
parser.add_argument('-W', '--whitebg', action='store_true', help='Fill the background with white instead of black.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
maskfile=args.maskfile
invert=args.invert
rgb=args.rgb
whitebg=args.whitebg
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

def cmd(image_, mask_):
	# gray image
	if image_.ndim==2:
		reshape_channel=False
		imagedata=image_[None]
		nC,nH,nW=imagedata.shape

	# multi-channel image, including RGB
	elif image_.ndim==3:
		reshape_channel=image_.shape[-1]<10 # heuristic: reshape to (nC,nH,nW)
		imagedata=image_.transpose(2, 0, 1) if reshape_channel else image_
		nC,nH,nW=imagedata.shape

	# mask out
	with MemoryFile() as memfile:
		with memfile.open(
			driver='GTiff',
			width=nW,
			height=nH,
			dtype=image_.dtype,
			count=nC,
			transform=None,
			crs=None,
			) as dataset:

			# Write image into dataset
			for idxC in range(nC):
				dataset.write(imagedata[idxC, :, :], idxC+1)

			masked_image,_=mask_tool(
				dataset,
				shapes=mask_['geometry'].tolist(),
				crop=False,
				pad=False,
				invert=invert,
				filled=True,
				nodata=np.iinfo(imagedata.dtype).max if whitebg else None, # white or black background
				all_touched=False,
				)
			print(f"==>mask_tool(), {masked_image.shape}", flush=True)

			if image_.ndim==2: # individual channel
				masked_image=masked_image[0, :, :] # only one bind for gray image
			elif reshape_channel:
				masked_image=masked_image.transpose(1, 2, 0) # reshape back to RGB: (nH, nW, 3)

			return masked_image

# 1. mask input
if maskfile.endswith('.parquet'):
	mask=gpd.read_parquet(maskfile)
elif maskfile.endswith('.geojson'):
	mask=gpd.read_file(maskfile)
print(f"==> {mask=}", flush=True)

# 2. image input
image=tifffile.imread(infile, is_ome=False, level=0)
print(f"==> {image.shape=}, {image.dtype=}", flush=True)

# 3. mask image
masked_image=cmd(image, mask)
print(f"==> {masked_image.shape=}, {masked_image.dtype=}", flush=True)

rgb_infer=(masked_image.ndim==3 and masked_image.shape[-1] == 3)
if rgb_infer != rgb:
	print(f"Warning: -r|--rgb ({rgb=}) is not used. Use inferred rgb ({rgb_infer=}).", flush=True)

# 4. save
tifffile.imwrite(
	f"{outdir}/{bname}.tif",
	masked_image,
	photometric='rgb' if rgb_infer else 'minisblack',
	compression='lzw',
	bigtiff=False,
	ome=False,
	)
