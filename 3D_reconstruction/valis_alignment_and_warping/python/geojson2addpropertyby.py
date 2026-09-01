#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Merge columns of a headed metadata table onto the features, matched on one property.

import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-k', '--propertykey', action='append', help='Property to match, repeatable. The first one present is used.')
parser.add_argument('-m', '--metafile', required=True, help='Headed metadata file, tab delimited.')
parser.add_argument('-K', '--metakey', required=True)
parser.add_argument('-v', '--metavalue', action='append', help='Metadata column to add, repeatable. Default: all.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
propertykey=args.propertykey if args.propertykey else ['cell_id']
metafile=args.metafile
metakey=args.metakey
metavalue=args.metavalue
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

if infile.endswith('.parquet'):
	indata = gpd.read_parquet(infile)
elif infile.endswith('.geojson'):
	indata = gpd.read_file(infile)
else:
	raise ValueError(f"Unsupported file extension: {infile}")

print(f"==> Loaded {len(indata)} features from {infile}", flush=True)

metadata = pd.read_csv(metafile, sep='\t', header=0)
if metavalue:
	metadata=metadata[[metakey]+list(metavalue)]
print(f"==> Loaded {len(metadata)} metadata rows from {metafile}", flush=True)

props_to_check = list(propertykey)
valid_props = list(set(props_to_check).intersection(indata.columns))
valid_prop = valid_props[0] if valid_props else None
if valid_prop is None:
	raise ValueError(f"None of the specified properties {props_to_check} found in {infile}. Available columns: {indata.columns}")

indata[valid_prop] = indata[valid_prop].astype(str)
metadata[metakey] = metadata[metakey].astype(str)
indata = indata.merge(metadata, left_on=valid_prop, right_on=metakey, how='left')

indata.to_file(f"{outdir}/{bname}.geojson", driver='GeoJSON')
