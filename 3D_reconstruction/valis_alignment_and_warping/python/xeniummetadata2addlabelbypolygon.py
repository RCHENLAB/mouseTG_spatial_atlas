#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Label each cell of a metadata table by the polygon it falls into, per section.
# Used to split the cells of a section into the left and the right trigeminal ganglion.

import argparse
from collections import defaultdict
from pathlib import Path
import geopandas as gpd
import pandas as pd
from joblib import Parallel, delayed
from shapely import affinity
from shapely.geometry import Point

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-m', '--maskfile', action='append', required=True, help='Mask .parquet or .geojson file, repeatable.')
parser.add_argument('-i', '--subsetid', action='append', required=True, help='Metadata value selecting the rows of each mask, repeatable.')
parser.add_argument('-n', '--labelname', action='append', required=True, help='Label written for each mask, repeatable.')
parser.add_argument('-c', '--subsetcolumn', default='sampleid')
parser.add_argument('-l', '--labelheader', default='tglabel')
parser.add_argument('-u', '--unassignedname', default='Unassigned')
parser.add_argument('-s', '--scale', type=float, default=0.2125, help='Micron per pixel of the polygon coordinates.')
parser.add_argument('-x', '--xlocation', default='x')
parser.add_argument('-y', '--ylocation', default='y')
parser.add_argument('-t', '--numthreads', type=int, default=12)
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
maskfile=args.maskfile
subsetid=args.subsetid
labelname=args.labelname
subsetcolumn=args.subsetcolumn
labelheader=args.labelheader
unassignedname=args.unassignedname
scale=args.scale
xlocation=args.xlocation
ylocation=args.ylocation
numthreads=args.numthreads
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

## Transform transcript
def xy_scale(geom, scalef):
	geom_tf=affinity.scale(geom, xfact=scalef, yfact=scalef, origin=(0, 0))
	return geom_tf

def cmd(group_name, group_data):
	result=group_data.copy()
	result[labelheader]=unassignedname

	if group_name not in maskdict:
		print(f"Warning: {group_name=} is not in {maskdict=}", flush=True)
		return result

	# Bugfix: Several mask files for one sampleid
	for mfile, lname in maskdict[group_name]:
		# Loop mask
		# 1. Mask
		if mfile.endswith('.parquet'):
			mask=gpd.read_parquet(mfile)
		elif mfile.endswith('.geojson'):
			mask=gpd.read_file(mfile)
		print(f"==> {group_name=}, {mask=}, {mask.columns=}", flush=True)

		# 2. Create points
		if {xlocation, ylocation}.issubset(group_data.columns):
			geometry=[Point(xy) for xy in zip(group_data[xlocation], group_data[ylocation])]
		else:
			geometry=[Point(xy) for xy in zip(group_data.iloc[:, 1], group_data.iloc[:, 0])] # (y,x)

		geom_point=gpd.GeoDataFrame(geometry=geometry, crs=mask.crs)

		# 3. Scale geom_point
		geom_point['geometry']=geom_point['geometry'].apply(lambda geom: xy_scale(geom, 1.0/scale))
		print(f"Info: xy_scale(), {geom_point=}, {geom_point.columns=}", flush=True)

		# 4. Spatial join
		point_joined=gpd.sjoin(
			geom_point,
			mask,
			how='left',
			predicate='within',
			)

		# 5. Add label
		inside_mask=point_joined.index_right.notna()
		result.loc[group_data.index[inside_mask], labelheader]=lname

	return result

# 1. Metadata
indata=pd.read_csv(infile, sep='\t', header=0)
print(f"==> {indata=}, {indata.columns=}", flush=True)

# 2. subsetid: (maskfile, labelname)
maskdict=defaultdict(list)
for sid,mfile,lname in zip(subsetid, maskfile, labelname):
	maskdict[sid].append((mfile, lname))
print(f"==> {maskdict=}", flush=True)

# 3. Main()
result_jobs=Parallel(n_jobs=numthreads)(
	delayed(cmd)(group_name, group_data)
	for group_name, group_data in indata.groupby(subsetcolumn)
	)

results=pd.concat(result_jobs, ignore_index=True)
print(f"==> {results=}", flush=True)
results.to_csv(f"{outdir}/{bname}.txt.gz", sep='\t', index=False)
