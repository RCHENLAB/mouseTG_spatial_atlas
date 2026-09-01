#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Warp the geometries of one section from its original image space into the aligned stack,
# using the registrar written by the Valis registration.

import argparse
from pathlib import Path
import geopandas as gpd
from valis import registration

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-r', '--registrar', required=True, help='Saved registrar .pickle file.')
parser.add_argument('-s', '--slidename', required=True, help='Slide name of the section inside the registrar.')
parser.add_argument('-c', '--crop', default='overlap', choices=['all', 'overlap', 'reference'])
parser.add_argument('infile')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
modelfile=args.registrar
slidename=args.slidename
crop=args.crop
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

# registrar
registrar=registration.load_registrar(modelfile)
print(f"{registrar=}", flush=True)
slide=registrar.get_slide(slidename)
print(f"{slide=}", flush=True)

# warped geojson
warped_geojson=slide.warp_geojson(
	geojson_f=infile,
	slide_level=0,
	pt_level=0,
	non_rigid=True,
	crop=crop,
	)
print(f"{warped_geojson=}", flush=True)

# Save warped geojson
warped_gdf=gpd.GeoDataFrame.from_features(warped_geojson['features'])
print(f"{warped_gdf=}", flush=True)
warped_gdf.to_file(f"{outdir}/{bname}.geojson")
