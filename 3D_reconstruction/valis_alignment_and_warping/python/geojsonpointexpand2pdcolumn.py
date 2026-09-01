#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Expand point geometries into x/y/z columns and drop the geometry, giving a plain table.

import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-p', '--prefix', default='', help='Prefix for the coordinate columns, e.g. warp_.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
prefix=args.prefix
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

if infile.endswith('.parquet'):
	indata = gpd.read_parquet(infile)
elif infile.endswith('.geojson') or infile.endswith('.json'):
	indata = gpd.read_file(infile)
else:
	raise ValueError(f"Unsupported file extension: {infile}")

print(f"==> Loaded {len(indata)} features from {infile}", flush=True)

x = indata.geometry.x
y = indata.geometry.y
indata[f"{prefix}x"] = x
indata[f"{prefix}y"] = y
if indata.geometry.has_z.any():
	z = indata.geometry.z
	indata[f"{prefix}z"] = z

df = pd.DataFrame(indata.drop(columns='geometry'))

print(f"==> Converted data has {len(df)} rows. Saving to {outdir}/{bname}.txt.gz", flush=True)
df.to_csv(f"{outdir}/{bname}.txt.gz", sep='\t', index=False, na_rep='NA')
