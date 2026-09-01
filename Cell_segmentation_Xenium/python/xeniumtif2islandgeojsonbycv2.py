#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Detect high-intensity islands (e.g. interior-RNA enriched neuron regions) and write mask images and outer contours.

import argparse
from pathlib import Path
import numpy as np
import cv2
import tifffile
import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Polygon

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-k', '--kernelsize', type=int, default=101)
parser.add_argument('-p', '--expansionsize', type=int, default=100)
parser.add_argument('-m', '--minarea', type=float, default=1000)
parser.add_argument('-c', '--channel', type=int, default=0)
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
kernelsize=args.kernelsize
expansionsize=args.expansionsize
minarea=args.minarea
channel=args.channel
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

def array2hist(intensity, outfile):
	plt.figure(figsize=(5, 5), dpi=50)
	plt.hist(intensity, bins=256)
	plt.xlabel('Intensity')
	plt.ylabel("Frequency")
	plt.savefig(outfile, bbox_inches='tight')
	plt.close()

def mask2polygongeojson(maskmtx, outfile):
	contours, _=cv2.findContours(maskmtx, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	polygons=[]
	for contour in contours:
		coords=[(point[0][0], point[0][1]) for point in contour]
		coords+=[coords[0]] # circular coordinates
		polygons+=[Polygon(coords)]
	geo_df=gpd.GeoDataFrame(geometry=polygons)
	geo_df.to_file(outfile, driver='GeoJSON')

image=tifffile.imread(infile, is_ome=False, level=0)
print(f"==> {image.shape=}, {image.dtype=}", flush=True)

if image.ndim==3: # use one channel only
	image=image[channel, :, :]

# 16bit to 8bit
if image.dtype!=np.uint8:
	image=np.array((image*1.0/image.max())*255, dtype=np.uint8)
	print(f"==> 8bit: {image.shape=}, {image.dtype=}", flush=True)

array2hist(image.ravel(), f"{outdir}/{bname}_hist_original.pdf")

# Otsu's thresholding after Gaussian filtering
blur=cv2.GaussianBlur(image, (11, 11), 0)
array2hist(blur.ravel(), f"{outdir}/{bname}_hist_blur.pdf")

# thresholding
_, binary=cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

# morphology
kernel=np.ones((kernelsize, kernelsize), np.uint8)
closed=cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

# islands
num_labels, labels, stats, centroids=cv2.connectedComponentsWithStats(closed, connectivity=8)
print(f"Number of high-intensity islands detected: {num_labels-1}", flush=True)

# save the mask
mask=np.zeros_like(image)
for i in range(1, num_labels):
	if stats[i, cv2.CC_STAT_AREA]>=minarea:
		mask[labels==i]=255

tifffile.imwrite(
	f"{outdir}/{bname}_orimask.tif",
	mask,
	bigtiff=False,
	ome=False,
	compression='LZW',
	photometric='MINISBLACK'
	)
mask2polygongeojson(mask, f"{outdir}/{bname}_orimask.geojson")

# expand the mask
kernel_exp=np.ones((expansionsize, expansionsize), np.uint8)
expanded_mask=cv2.dilate(mask, kernel_exp, iterations=1)

tifffile.imwrite(
	f"{outdir}/{bname}_expmask.tif",
	expanded_mask,
	bigtiff=False,
	ome=False,
	compression='LZW',
	photometric='MINISBLACK'
	)
mask2polygongeojson(expanded_mask, f"{outdir}/{bname}_expmask.geojson")
