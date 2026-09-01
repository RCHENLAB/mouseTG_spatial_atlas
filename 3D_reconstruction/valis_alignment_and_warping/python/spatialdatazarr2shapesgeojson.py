#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Export every shapes element of a SpatialData .zarr store as .geojson.

import argparse
from pathlib import Path
import spatialdata as sd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('infile', help='SpatialData .zarr store.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

# selection:shapes is needed for coordinate system
indata=sd.read_zarr(infile, selection=['shapes', 'tables'])
print(f"{indata=}", flush=True)

for key,value in indata.shapes.items():
	value.to_file(f"{outdir}/{bname}_{key}.geojson", driver='GeoJSON')
