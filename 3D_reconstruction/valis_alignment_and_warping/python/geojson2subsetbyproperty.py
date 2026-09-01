#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Keep the features whose property value is listed in an unheaded subset file.

import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-p', '--property', action='append', help='Property to match, repeatable. The first one present is used.')
parser.add_argument('-s', '--subsetfile', required=True, help='Unheaded subset file.')
parser.add_argument('-f', '--format', default='parquet', choices=['geojson', 'parquet', 'both'])
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
property=args.property if args.property else ['cell_id', 'index']
subsetfile=args.subsetfile
format=args.format
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

if infile.endswith('.parquet'):
	indata = gpd.read_parquet(infile)
elif infile.endswith('.geojson'):
	indata = gpd.read_file(infile)
else:
	raise ValueError(f"Unsupported file extension: {infile}")

print(f"==> Loaded {len(indata)} features from {infile}", flush=True)

subset_df = pd.read_csv(subsetfile, header=None)
subset_items = set(subset_df[0].astype(str))

print(f"==> Loaded {len(subset_items)} items from {subsetfile} to subset", flush=True)

props_to_check = [property] if isinstance(property, str) else property
valid_props = list(set(props_to_check).intersection(indata.columns))
valid_prop = valid_props[0] if valid_props else None
if valid_prop is None:
	raise ValueError(f"None of the specified properties {props_to_check} found in {infile}. Available columns: {indata.columns}")

indata = indata[indata[valid_prop].astype(str).isin(subset_items)]

print(f"==> Subset contains {len(indata)} features", flush=True)

if format in ('geojson', 'both'):
	outfile=f"{outdir}/{bname}.geojson"
	indata.to_file(outfile, driver='GeoJSON')
	print(f"==> Wrote {len(indata)} features to {outfile}", flush=True)
if format in ('parquet', 'both'):
	outfile=f"{outdir}/{bname}.parquet"
	indata.to_parquet(outfile)
	print(f"==> Wrote {len(indata)} features to {outfile}", flush=True)
