#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Export the pixel coordinates of selected transcripts from a Xenium transcripts.parquet.

import argparse
from pathlib import Path
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-l', '--level', type=int, default=0, choices=range(0, 8), help='Image pyramid level for the scale factor.')
parser.add_argument('-s', '--symbol', action='append', required=True, help='Gene symbol, repeatable.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
symbols=args.symbol
infile=args.infile
scale=0.2125*(2 ** args.level) # micron per pixel
Path(outdir).mkdir(parents=True, exist_ok=True)

indata=pd.read_parquet(infile)
print(f"Info: {indata=}, {indata.columns=}")

indata=indata[indata['feature_name'].isin(symbols)].copy()
print(f"Info: in symbol, {indata=}, {indata.columns=}")

result=indata[['y_location', 'x_location']].copy()
result.rename({'x_location': 'axis-0', 'y_location': 'axis-1'}, axis=1, inplace=True)
result[['axis-0', 'axis-1']] *= 1.0/scale
print(f"Info: {result=}, {result.columns=}")

result.to_csv(f"{outdir}/{bname}.csv", index=False)
