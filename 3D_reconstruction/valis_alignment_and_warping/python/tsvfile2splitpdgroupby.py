#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Split a headed table into one file per group, optionally keeping only the rows matching a filter.
# With --idcolumn an unheaded list of that column is written next to each group file.

import argparse
from pathlib import Path
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-c', '--column', required=True, help='Column to group by, e.g. sampleid.')
parser.add_argument('-f', '--filter', help='Keep only the rows matching column=value.')
parser.add_argument('-i', '--idcolumn', help='Also write an unheaded list of this column per group.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
Path(outdir).mkdir(parents=True, exist_ok=True)

indata=pd.read_csv(args.infile, sep='\t', header=0, dtype=str)
print(f"==> Loaded {len(indata)} rows from {args.infile}", flush=True)

if args.filter:
	column,value=args.filter.split('=', 1)
	indata=indata[indata[column]==value]
	print(f"==> {len(indata)} rows with {column}={value}", flush=True)

for name,group in indata.groupby(args.column):
	group.to_csv(f"{outdir}/{name}_metadata.txt.gz", sep='\t', index=False)
	if args.idcolumn:
		group[[args.idcolumn]].to_csv(f"{outdir}/{name}.txt.gz", sep='\t', index=False, header=False)
	print(f"==> {name}: {len(group)} rows", flush=True)
