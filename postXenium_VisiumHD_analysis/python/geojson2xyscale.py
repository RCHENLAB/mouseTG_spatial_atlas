#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Scale the x and y coordinates of a GeoJSON or GeoParquet about the origin.

import argparse
from pathlib import Path
import geopandas as gpd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-x', '--scalex', type=float, default=1.0)
parser.add_argument('-y', '--scaley', type=float, default=1.0)
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
scalex=args.scalex
scaley=args.scaley
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

if infile.endswith('.parquet'):
	indata = gpd.read_parquet(infile)
elif infile.endswith('.geojson'):
	indata = gpd.read_file(infile)
else:
	raise ValueError(f"Unsupported file extension: {infile}")

print(f"==> {indata=}, {indata.columns=}", flush=True)

indata['geometry'] = indata.geometry.scale(xfact=scalex, yfact=scaley, origin=(0, 0))
print(f"==> Transformed: {indata=}, {indata.columns=}", flush=True)

if 'index' in indata.columns:
	indata = indata.set_index('index', drop=True)
elif 'id' in indata.columns:
	indata = indata.set_index('id', drop=True)

indata.index.name='id'
print(f"Info: {indata=}, {indata.columns=}", flush=True)

with open(f"{outdir}/{bname}.geojson", "w") as f:
	f.write(indata.to_json())
