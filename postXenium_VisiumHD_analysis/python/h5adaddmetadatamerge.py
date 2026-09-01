#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Merge a headed metadata table into adata.obs on a shared key.
# The aggregated Visium HD cells are keyed by the Xenium cell_id, so Xenium annotations
# are attached with a left merge and missing cells are labelled with --nastring.

import argparse
from pathlib import Path
import anndata as ad
import pandas as pd
import scanpy as sc

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-m', '--metafile', required=True, help='Headed metadata file, tab delimited.')
parser.add_argument('-k', '--key', default='_index_', help="obs key to merge on; '_index_' uses the obs index.")
parser.add_argument('-r', '--rightkey', help='Metadata column to merge on. Default: the first column.')
parser.add_argument('-t', '--type', default='left', choices=['left', 'right', 'outer', 'inner'])
parser.add_argument('-N', '--nastring', default='Unassigned')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
Path(outdir).mkdir(parents=True, exist_ok=True)

x=ad.read_h5ad(args.infile)
print(f"Info: {x=}", flush=True)

metadata=pd.read_csv(args.metafile, header=0, sep='\t', dtype=str)
rightkey=args.rightkey if args.rightkey else metadata.columns[0]
metadata=metadata.drop_duplicates(subset=rightkey)
print(f"Info: {metadata=}, {metadata.columns=}, {rightkey=}", flush=True)

obs=x.obs.copy()
obs.insert(loc=0, column='_index_', value=obs.index.astype(str))
merged=obs.merge(metadata, how=args.type, left_on=args.key, right_on=rightkey)
merged=merged.fillna(args.nastring)
merged.index=merged['_index_']
merged.index.name=None
merged=merged.drop(columns=['_index_'])

x=x[merged.index].copy()
x.obs=merged
print(f"Info: merged, {x.obs=}, {x.obs.columns=}", flush=True)

sc.write(filename=f"{outdir}/{bname}.h5ad", adata=x)
x.obs.insert(loc=0, column='obs_index', value=x.obs.index)
x.obs.to_csv(f"{outdir}/{bname}_obs.txt.gz", sep='\t', index=False)
x.var.insert(loc=0, column='var_index', value=x.var.index)
x.var.to_csv(f"{outdir}/{bname}_var.txt.gz", sep='\t', index=False)
