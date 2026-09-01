#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Stack the 2D geometries of consecutive sections into one 3D point cloud, one z per section.

import argparse
from pathlib import Path
import geopandas as gpd
from joblib import Parallel, delayed
from shapely.ops import transform

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-s', '--start', type=float, default=0, help='First z, in the unit of the coordinates.')
parser.add_argument('-p', '--step', type=float, default=12, help='Spacing between sections along z.')
parser.add_argument('-t', '--numthreads', type=int, default=8)
parser.add_argument('-n', '--backend', default='threading', choices=['threading', 'loky'])
parser.add_argument('-i', '--id', action='append', help='Name of each section, repeatable and in input order.')
parser.add_argument('-N', '--idname', default='slicename', help='Property holding the section name.')
parser.add_argument('-j', '--join', default='outer', choices=['inner', 'outer'])
parser.add_argument('infile', nargs='+', help='Section files in serial order.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
start=args.start
step=args.step
numthreads=args.numthreads
backend=args.backend
id=args.id if args.id else []
idname=args.idname
join=args.join
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

def cmd(name, file, z_value, idname):
	print(f"Start running: {name=}, {file=}", flush=True)

	if file.endswith('.parquet'):
		indata = gpd.read_parquet(file)
	elif file.endswith('.geojson'):
		indata = gpd.read_file(file)
	else:
		raise ValueError(f"Unsupported file extension: {file}")

	indata.geometry = indata.geometry.map(lambda geom: transform(lambda x, y, z=None: (x, y, z_value), geom))
	indata[idname] = name

	print(f"Finish running: {name=}, {file=}", flush=True)

	return indata

if len(id) != len(infile):
	id = [Path(file).stem for file in infile]

z_values = [start + i * step for i in range(len(infile))]

slicedata = Parallel(n_jobs=numthreads, backend=backend)(
	delayed(cmd)(name, file, z_value, idname)
	for name, file, z_value in zip(id, infile, z_values)
)

result = gpd.pd.concat(slicedata, axis=0, join=join, ignore_index=True)
print(f"Info: {result=}", flush=True)

result.to_parquet(f"{outdir}/{bname}.parquet")
