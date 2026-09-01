#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Aggregate Visium HD bins into segmentation polygons: every bin centre falling inside a polygon
# contributes its counts to that polygon, giving a cell-by-gene matrix keyed by the polygon id.

import argparse
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('-s', '--segmentation', required=True, help='Segmentation polygon file in GeoJSON or Parquet format.')
parser.add_argument('-p', '--spatialkey', default='spatial', help='obsm key holding the X,Y bin coordinates.')
parser.add_argument('-x', '--xcol', help='obs column for X, alternative to --spatialkey.')
parser.add_argument('-y', '--ycol', help='obs column for Y, alternative to --spatialkey.')
parser.add_argument('-i', '--idkey', help='Segmentation column used as output barcode. E.g. "id".')
parser.add_argument('infile', help='Binned Visium HD .h5ad.')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
segmentation=args.segmentation
spatialkey=args.spatialkey
xcol=args.xcol
ycol=args.ycol
idkey=args.idkey
infile=args.infile
Path(outdir).mkdir(parents=True, exist_ok=True)

import json

import anndata as ad
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, csr_matrix, issparse
import scanpy as sc


def jsonscalar(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return value


def buildbarcodes(features, idkey):
    barcode=pd.Series(pd.NA, index=features.index, dtype='object')
    if idkey is not None and idkey in features.columns:
        barcode=features[idkey].replace('', pd.NA)
    fallback=features.index.to_series().map(lambda index: f'polygon_{index:06d}')
    return barcode.fillna(fallback).astype(str)


def loadfeatures(segmentation, idkey):
    suffixes={suffix.lower() for suffix in Path(segmentation).suffixes}
    if '.parquet' in suffixes:
        features=gpd.read_parquet(segmentation)
    elif '.geojson' in suffixes or '.json' in suffixes:
        features=gpd.read_file(segmentation)
    else:
        raise ValueError(f'Unsupported segmentation format in {segmentation!r}. Expected .geojson or .parquet.')

    if 'geometry' not in features.columns:
        raise ValueError(f'Segmentation file {segmentation!r} does not contain a geometry column.')

    features=features.loc[features.geometry.notna()].copy()
    features=features.loc[~features.geometry.is_empty].copy()
    features=features.reset_index(drop=True)
    if features.empty:
        raise ValueError(f'No valid polygon features were found in {segmentation!r}.')

    polygons=features.copy()
    for column in polygons.columns:
        if column == 'geometry':
            continue
        polygons[column]=polygons[column].map(jsonscalar)
    polygons['barcode']=buildbarcodes(polygons, idkey=idkey)
    polygons['polygon_area']=polygons.geometry.area
    centroids=polygons.geometry.centroid
    polygons['centroid_x']=centroids.x
    polygons['centroid_y']=centroids.y
    if polygons['barcode'].duplicated().any():
        duplicates=', '.join(polygons.loc[polygons['barcode'].duplicated(), 'barcode'].astype(str).head(10))
        raise ValueError(f'Segmentation barcodes are not unique. Example duplicate values: {duplicates}')
    return polygons.set_index('barcode', drop=True)


def getcoords(adata, spatialkey, xcol, ycol):
    if xcol is not None and ycol is not None:
        missing=[column for column in (xcol, ycol) if column not in adata.obs.columns]
        if missing:
            raise KeyError(f'Missing coordinate columns in obs: {missing}')
        coords=adata.obs.loc[:, [xcol, ycol]].to_numpy()
    elif spatialkey in adata.obsm:
        coords=np.asarray(adata.obsm[spatialkey])
        if coords.ndim != 2 or coords.shape[1] < 2:
            raise ValueError(f'obsm[{spatialkey!r}] must be a 2D array with at least two columns.')
        coords=coords[:, :2]
    else:
        raise KeyError(f'Unable to find coordinates. Provide --xcol/--ycol or ensure obsm[{spatialkey!r}] exists.')

    return np.asarray(coords, dtype=float)


def assignpoints(coords, polygons):
    assignments=np.full(coords.shape[0], -1, dtype=int)
    polygonframe=polygons.loc[:, ['geometry']]
    points=gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(coords[:, 0], coords[:, 1]),
        crs=polygonframe.crs,
    )
    joined=gpd.sjoin(
        points,
        polygonframe,
        how='left',
        predicate='within',
    )
    print(f"Info: joined, {joined=}", flush=True)

    joinkey='index_right'
    if joinkey not in joined.columns:
        joinkey=polygons.index.name or joinkey
    if not joined.empty:
        joined=joined.dropna(subset=[joinkey])
        if not joined.empty:
            matchcounts=joined.groupby(level=0).size()
            ambiguouspoints=matchcounts[matchcounts > 1]
            if not ambiguouspoints.empty:
                examples=', '.join(map(str, ambiguouspoints.index[:10]))
                print(
                    f'INFO: Ignored {ambiguouspoints.shape[0]} points with multiple polygon assignments. '
                    f'Example point indices: {examples}',
                    flush=True,
                )
            uniquematches=joined.loc[joined.index.map(matchcounts) == 1, joinkey]
            assignments[uniquematches.index.to_numpy(dtype=int)]=polygons.index.get_indexer(uniquematches.to_numpy())
    unassignedcount=np.count_nonzero(assignments < 0)
    if unassignedcount > 0:
        print(f'INFO: Unassigned points: {unassignedcount} of {coords.shape[0]}', flush=True)

    return assignments


def aggregatematrix(matrix, assignments, ngroups):
    mask=assignments >= 0
    if not np.any(mask):
        return csr_matrix((ngroups, matrix.shape[1]), dtype=matrix.dtype)

    groupmatrix=coo_matrix(
        (
            np.ones(mask.sum(), dtype=np.int8),
            (assignments[mask], np.flatnonzero(mask)),
        ),
        shape=(ngroups, assignments.shape[0]),
    ).tocsr()

    if issparse(matrix):
        return groupmatrix @ matrix
    return groupmatrix @ csr_matrix(matrix)


adata=ad.read_h5ad(infile)
print(f"Info: read_h5ad(), Loaded AnnData {adata=}", flush=True)

coords=getcoords(adata, spatialkey=spatialkey, xcol=xcol, ycol=ycol)
print(f"Info: getcoords(), Loaded coordinates {coords=} ", flush=True)

polygons=loadfeatures(segmentation=segmentation, idkey=idkey)
print(f"Info: loadfeatures(), Loaded polygons {polygons=}", flush=True)

assignments=assignpoints(coords=coords, polygons=polygons)
assignedcounts=np.bincount(assignments[assignments >= 0], minlength=polygons.shape[0])
obs=pd.DataFrame(polygons.drop(columns='geometry'))
obs['num_assigned_bins']=assignedcounts.astype(int)

outx=aggregatematrix(adata.X, assignments=assignments, ngroups=polygons.shape[0])

out=ad.AnnData(
    X=outx,
    obs=obs,
    var=adata.var.copy(),
)
out.var_names=adata.var_names.copy()
out.obsm[spatialkey]=obs.loc[:, ['centroid_x', 'centroid_y']].to_numpy()
print(f'INFO: num_polygons_with_bins: {int(np.count_nonzero(assignedcounts))}', flush=True)
print(f'INFO: num_assigned_bins: {int(np.count_nonzero(assignments >= 0))}', flush=True)

sc.write(filename=f"{outdir}/{bname}.h5ad", adata=out)
out.obs.insert(loc=0, column='obs_index', value=out.obs.index)
out.obs.to_csv(f"{outdir}/{bname}_obs.txt.gz", sep='\t', index=False)
out.var.insert(loc=0, column='var_index', value=out.var.index)
out.var.to_csv(f"{outdir}/{bname}_var.txt.gz", sep='\t', index=False)
