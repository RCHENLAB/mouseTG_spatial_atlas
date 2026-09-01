#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Merge columns of a headed metadata table into adata.obs, matched on a composite key
# such as (sampleid, cell_id). Cells without a match keep --nastring.

import argparse
from pathlib import Path
import anndata as ad
import pandas as pd
import scanpy as sc

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-m', '--metafile', required=True, help='Headed metadata file, tab delimited.')
parser.add_argument('-k', '--key', action='append', help='Key shared by both sides, repeatable.')
parser.add_argument('-l', '--leftkey', action='append', help='obs columns of the composite key, repeatable.')
parser.add_argument('-r', '--rightkey', action='append', help='Metadata columns of the composite key, repeatable.')
parser.add_argument('-v', '--metavalue', action='append', help='Metadata column to add, repeatable. Default: all.')
parser.add_argument('-t', '--type', default='left', choices=['left', 'right', 'outer', 'inner'])
parser.add_argument('-N', '--nastring', default='Unknown')
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
leftkey=args.key if args.key else args.leftkey
rightkey=args.key if args.key else args.rightkey
metavalue=args.metavalue
if not leftkey or not rightkey:
	raise ValueError("key is not defined. See -k|--key, -l|--leftkey and -r|--rightkey.")
Path(outdir).mkdir(parents=True, exist_ok=True)

x=ad.read_h5ad(args.infile)
print(f"==> Loaded {x=}", flush=True)

metadata=pd.read_csv(args.metafile, sep='\t', header=0)
if metavalue:
	metadata=metadata[list(rightkey)+list(metavalue)]
metadata=metadata.drop_duplicates(subset=list(rightkey))
print(f"==> Loaded {len(metadata)} metadata rows from {args.metafile}", flush=True)

obs=x.obs.copy()
obs.insert(loc=0, column='_obs_index_', value=obs.index.astype(str))
for lk in leftkey:
	if lk not in obs.columns:
		raise KeyError(f"'{lk}' is not in obs. Available columns: {list(obs.columns)}")
	obs[lk]=obs[lk].astype(str)
for rk in rightkey:
	metadata[rk]=metadata[rk].astype(str)

merged=obs.merge(metadata, left_on=leftkey, right_on=rightkey, how=args.type)
# Label the unmatched cells, but keep numeric columns numeric so that obs stays writable
for column in merged.columns:
	if merged[column].dtype==object:
		merged[column]=merged[column].fillna(args.nastring)
merged.index=merged['_obs_index_']
merged.index.name=None
merged=merged.drop(columns=['_obs_index_'])

x=x[merged.index].copy()
x.obs=merged
print(f"==> Merged {x.obs=}, {x.obs.columns=}", flush=True)

sc.write(filename=f"{outdir}/{bname}.h5ad", adata=x)
x.obs.insert(loc=0, column='obs_index', value=x.obs.index)
x.obs.to_csv(f"{outdir}/{bname}_obs.txt.gz", sep='\t', index=False)
x.var.insert(loc=0, column='var_index', value=x.var.index)
x.var.to_csv(f"{outdir}/{bname}_var.txt.gz", sep='\t', index=False)
