#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Harmonize neuron and non-neuron segmentation polygons for mouse TG Xenium.
#
# Scenarios of a neuron polygon relative to non-neuron polygons:
#   no overlap             -> keep the neuron polygon
#   contains non-neurons   -> keep the neuron polygon (non-neuron polygons are nuclei of that neuron)
#   within a non-neuron    -> drop the neuron polygon (weak neuron signal)
#   partial overlap        -> subtract the overlapping non-neuron region (satellite glia around a neuron)

import argparse
from pathlib import Path
import geopandas as gpd

parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-n', '--nonneuron', required=True, help='Non-neuron segmentation .parquet or .geojson file.')
parser.add_argument('infile', help='Neuron segmentation .parquet or .geojson file.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
nonneuron=args.nonneuron
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

if infile.endswith('.parquet'):
	minuend=gpd.read_parquet(infile)
elif infile.endswith('.geojson'):
	minuend=gpd.read_file(infile)
print(f"Info: {minuend=}, {minuend.columns=}")

if nonneuron.endswith('.parquet'):
	subtraend=gpd.read_parquet(nonneuron)
elif nonneuron.endswith('.geojson'):
	subtraend=gpd.read_file(nonneuron)
print(f"Info: {subtraend=}, {subtraend.columns=}")

def leftindex(joined):
	# geopandas <1.0 exposes the left index as an 'index_left' column, later versions keep it as the index
	return joined['index_left'] if 'index_left' in joined.columns else joined.index

if minuend.crs!=subtraend.crs:
	subtraend=subtraend.to_crs(minuend.crs)

result=minuend.copy()

# Identify neurons with no overlap
non_overlapping=gpd.overlay(
	minuend,
	subtraend,
	how='difference',
	keep_geom_type=True,
	)

# Identify neurons fully contained within non-neurons
contained_neurons=gpd.sjoin(
	minuend,
	subtraend,
	how='inner',
	predicate='within',
)
# Exclude neurons contained within non-neurons
result=result[~result.index.isin(leftindex(contained_neurons))]

# Identify neurons fully containing non-neurons
containing_neurons=gpd.sjoin(
	minuend,
	subtraend,
	how='inner',
	predicate='contains',
)
# Keep containing neurons and non-contained neurons
result=result[
	result.index.isin(leftindex(containing_neurons)) |
	~result.index.isin(leftindex(contained_neurons))
	]

# Subtract overlapping non-neuron regions from partially overlapping neurons
contained_nonneurons=gpd.sjoin(
	subtraend,
	result,
	how='inner',
	predicate='within',
)
non_contained_nonneurons=subtraend[~subtraend.index.isin(contained_nonneurons.index)]

partial_overlaps=gpd.overlay(
	result,
	non_contained_nonneurons,
	how='intersection',
	keep_geom_type=True,
	)
if not partial_overlaps.empty:
	result=gpd.overlay(
		result,
		non_contained_nonneurons,
		how='difference',
		keep_geom_type=True,
		)

result=result[~result['geometry'].is_empty]
result=result.explode(index_parts=False)
result=result[result['geometry'].is_valid & ~result['geometry'].is_empty]
result['geometry']=result.buffer(0)
print(f"Info: {result=}, {result.columns=}")

result.to_file(f"{outdir}/{bname}.geojson", driver='GeoJSON')
