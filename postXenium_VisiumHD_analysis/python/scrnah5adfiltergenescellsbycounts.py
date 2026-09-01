#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Filter cells and genes of a .h5ad by minimum counts.

import argparse
from pathlib import Path
import scanpy as sc

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-c', '--mincount', type=int, default=1)
parser.add_argument('-k', '--keep', action='store_true', help='Keep the n_counts columns added by scanpy.')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
mincount=args.mincount
keep=args.keep
f=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

x=sc.read(f)
if keep:
	sc.pp.filter_cells(x, min_counts=mincount)
	sc.pp.filter_genes(x, min_counts=mincount)
else:
	cell_subset, _=sc.pp.filter_cells(x, min_counts=mincount, inplace=False)
	gene_subset, _=sc.pp.filter_genes(x, min_counts=mincount, inplace=False)
	x=x[cell_subset, gene_subset].copy()
print(x)

sc.write(filename=f'{outdir}/{bname}.h5ad', adata=x)
x.obs['barcode']=x.obs.index
x.obs.to_csv(f'{outdir}/{bname}_obs.txt.gz', sep='\t', index=False)
x.var['symbol']=x.var.index
x.var.to_csv(f'{outdir}/{bname}_var.txt.gz', sep='\t', index=False)
