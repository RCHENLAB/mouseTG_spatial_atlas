#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Merge columns of a headed metadata table onto the features, matched on a composite key.

import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-m', '--metafile', required=True, help='Headed metadata file, tab delimited.')
parser.add_argument('-k', '--key', action='append', help='Key shared by both sides, repeatable.')
parser.add_argument('-l', '--leftkey', action='append', help='Feature properties of the composite key, repeatable.')
parser.add_argument('-r', '--rightkey', action='append', help='Metadata columns of the composite key, repeatable.')
parser.add_argument('-v', '--metavalue', action='append', help='Metadata column to add, repeatable. Default: all.')
parser.add_argument('-t', '--type', default='inner', choices=['left', 'right', 'outer', 'inner'])
parser.add_argument('-N', '--nastring', default='Unknown')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
metafile=args.metafile
leftkey=args.key if args.key else args.leftkey
rightkey=args.key if args.key else args.rightkey
metavalue=args.metavalue
type=args.type
nastring=args.nastring
infile=args.infile
if not leftkey or not rightkey:
	raise ValueError("key is not defined. See -k|--key, -l|--leftkey and -r|--rightkey.")
Path(outdir).mkdir(parents=True, exist_ok=True)

if infile.endswith('.parquet'):
	indata = gpd.read_parquet(infile)
elif infile.endswith('.geojson') or infile.endswith('.json'):
	indata = gpd.read_file(infile)
else:
	raise ValueError(f"Unsupported file extension: {infile}")

print(f"==> Loaded {len(indata)} features from {infile}", flush=True)

metadata = pd.read_csv(metafile, sep='\t', header=0)
if metavalue:
	# Ensure rightkey columns are kept in metadata for merging
	metadata = metadata[list(rightkey) + list(metavalue)]
print(f"==> Loaded {len(metadata)} metadata rows from {metafile}", flush=True)

# Ensure keys are strings for consistent merging if they are IDs
for lk in leftkey:
	if lk in indata.columns:
		indata[lk] = indata[lk].astype(str)
for rk in rightkey:
	if rk in metadata.columns:
		metadata[rk] = metadata[rk].astype(str)

indata = indata.merge(metadata, left_on=leftkey, right_on=rightkey, how=type)

if nastring:
	indata = indata.fillna(nastring)

print(f"==> Merged data has {len(indata)} rows. Saving to {outdir}/{bname}.parquet", flush=True)
indata.to_parquet(f"{outdir}/{bname}.parquet")
