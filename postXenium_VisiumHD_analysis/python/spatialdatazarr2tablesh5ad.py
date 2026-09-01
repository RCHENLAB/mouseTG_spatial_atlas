#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Export every table of a SpatialData .zarr store as .h5ad plus obs/var tables.

import argparse
from pathlib import Path
import scanpy as sc
import spatialdata as sd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('infile', help='SpatialData .zarr store.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

# selection:shapes is needed for coordinate system
indata=sd.read_zarr(infile, selection=['shapes', 'tables'])
print(f"{indata=}", flush=True)

for key,value in indata.tables.items():
	sc.write(filename=f"{outdir}/{bname}_{key}.h5ad", adata=value)
	value.obs.insert(loc=0, column='obs_index', value=value.obs.index)
	value.obs.to_csv(f"{outdir}/{bname}_{key}_obs.txt.gz", sep='\t', index=False)
	value.var.insert(loc=0, column='var_index', value=value.var.index)
	value.var.to_csv(f"{outdir}/{bname}_{key}_var.txt.gz", sep='\t', index=False)
