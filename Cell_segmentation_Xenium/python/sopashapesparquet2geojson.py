#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Convert Sopa segmentation shapes.parquet to .geojson, optionally rescaling the coordinates.

import argparse
from pathlib import Path
import geopandas as gpd
from shapely import affinity

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-s', '--scale', type=float, default=1.0, help='Coordinates are divided by this factor.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
scale=args.scale
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

indata=gpd.read_parquet(infile)
print(indata)
indata.info(verbose=True)

# Transformation
def xy_scale(geom, scalef):
	geom_tf=affinity.scale(geom, xfact=1.0/scalef, yfact=1.0/scalef, origin=(0, 0))
	return geom_tf

indata['geometry']=indata['geometry'].apply(lambda geom: xy_scale(geom, scale))
print(f"Info: xy_scale(), {indata=}, {indata.columns=}")

indata.to_file(f"{outdir}/{bname}.geojson", driver='GeoJSON')
