#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Keep (or drop, with --invert) the cells whose obs label is one of the given values.

import argparse
from pathlib import Path
import scanpy as sc

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-l', '--label', required=True, help='obs column holding the cell type.')
parser.add_argument('-v', '--value', action='append', required=True, help='Value to keep, repeatable.')
parser.add_argument('-n', '--invert', action='store_true', help='Drop the listed values instead.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
label=args.label
values=args.value
invert=args.invert
f=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

x=sc.read(f)

# bug fix the int columns
if x.obs[label].dtype==int:
	x.obs[label]=x.obs[label].astype(str)

if invert:
	x=x[~x.obs[label].isin(values)].copy()
else:
	x=x[x.obs[label].isin(values)].copy()

## Bug fix
if '_index' in x.var_keys():
	x.var.set_index('_index', inplace=True)

print(x)

sc.write(filename=f'{outdir}/{bname}.h5ad', adata=x)
x.obs['barcode']=x.obs.index
x.obs.to_csv(f'{outdir}/{bname}_obs.txt.gz', sep='\t', index=False)
x.var['symbol']=x.var.index
x.var.to_csv(f'{outdir}/{bname}_var.txt.gz', sep='\t', index=False)
