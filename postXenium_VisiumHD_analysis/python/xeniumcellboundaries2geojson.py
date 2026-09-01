#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Convert the cell_boundaries.parquet of a Xenium bundle to a GeoJSON of cell polygons.
# Coordinates stay in microns; the feature id is the Xenium cell_id.

import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-i', '--idcolumn', default='cell_id')
parser.add_argument('-x', '--xcolumn', default='vertex_x')
parser.add_argument('-y', '--ycolumn', default='vertex_y')
parser.add_argument('infile', help='cell_boundaries.parquet of a Xenium bundle.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
idcolumn=args.idcolumn
xcolumn=args.xcolumn
ycolumn=args.ycolumn
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

indata=pd.read_parquet(infile)
print(f"Info: {indata=}, {indata.columns=}", flush=True)

if isinstance(indata[idcolumn].iloc[0], bytes):
	indata[idcolumn]=indata[idcolumn].str.decode('utf-8')

polygons=[]
ids=[]
for cellid, vertices in indata.groupby(idcolumn, sort=False):
	coords=list(zip(vertices[xcolumn], vertices[ycolumn]))
	if len(coords)<3:
		continue
	if coords[0]!=coords[-1]:
		coords+=[coords[0]] # circular coordinates
	polygons+=[Polygon(coords)]
	ids+=[cellid]

result=gpd.GeoDataFrame({'id': ids}, geometry=polygons)
result=result.set_index('id', drop=True)
print(f"Info: {result=}, {result.columns=}", flush=True)

# Space Ranger rejects a FeatureCollection carrying extra 'name'/'crs' keys, so write with to_json()
with open(f"{outdir}/{bname}.geojson", "w") as f:
	f.write(result.to_json())
