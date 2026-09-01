#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Keep non-neuron polygons whose non-neuron marker transcript fraction is at least --ratio.

import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-n', '--nonneuron', required=True, help='Non-neuron transcript .csv or .parquet file.')
parser.add_argument('-N', '--neuron', required=True, help='Neuron transcript .csv or .parquet file.')
parser.add_argument('-r', '--ratio', type=float, default=0.1)
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
nonneuron=args.nonneuron
neuron=args.neuron
ratio=args.ratio
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

# Input polygons
if infile.endswith('.parquet'):
	indata=gpd.read_parquet(infile)
elif infile.endswith('.geojson'):
	indata=gpd.read_file(infile)
print(f"Info: {indata=}, {indata.columns=}")

def transcriptfile2geodf(file):
	if file.endswith('.parquet'):
		transcriptdata=gpd.read_parquet(file)
	elif file.endswith('.csv'):
		transcriptdata=pd.read_csv(file)
	print(f"Info: {transcriptdata=}, {transcriptdata.columns=}")

	if {'x_location', 'y_location'}.issubset(transcriptdata.columns):
		geometry=[Point(xy) for xy in zip(transcriptdata['x_location'], transcriptdata['y_location'])]
	else:
		geometry=[Point(xy) for xy in zip(transcriptdata.iloc[:, 1], transcriptdata.iloc[:, 0])] # (y, x) by xeniumtranscriptsparquet2csv
	transcriptdata=gpd.GeoDataFrame(geometry=geometry, crs=indata.crs)
	return transcriptdata

# Non-neuron transcripts
transcript_nonneuron=transcriptfile2geodf(nonneuron)
# Neuron transcripts
transcript_neuron=transcriptfile2geodf(neuron)

# Perform spatial join to count transcript_nonneuron points in each polygon
nonneuron_joined=gpd.sjoin(
	indata,
	transcript_nonneuron,
	how='left',
	predicate='contains',
	)
nonneuron_counts=nonneuron_joined.groupby(nonneuron_joined.index).size().reindex(indata.index, fill_value=0)
indata['nonneuron_count']=nonneuron_counts

# Perform spatial join to count transcript_neuron points in each polygon
neuron_joined=gpd.sjoin(
	indata,
	transcript_neuron,
	how='left',
	predicate='contains',
	)
neuron_counts=neuron_joined.groupby(neuron_joined.index).size().reindex(indata.index, fill_value=0)
indata['neuron_count']=neuron_counts

# Calculate the ratio: nonneuron_count / (nonneuron_count + neuron_count)
indata['ratio']=indata.apply(
	lambda row: row['nonneuron_count'] / (row['nonneuron_count']+row['neuron_count'])
	if (row['nonneuron_count']+row['neuron_count'])>0 else 10.0, # not create a hole
	axis=1,
)
indata.to_parquet(f"{outdir}/{bname}.parquet")
print(f"Info: {indata=}, {indata.columns=}")

result=indata[indata['ratio']>=ratio].copy()
result=result.drop(columns=['nonneuron_count', 'neuron_count', 'ratio'])
print(f"Info: ratio, {result=}, {result.columns=}")

result.to_file(f"{outdir}/{bname}.geojson", driver='GeoJSON')
