#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:
"""Assemble the merged 3D object (step 03).

Re-read the same warped_allcells.h5ad and the chains from step 02, then build one
AnnData in which:
  * each chain -> one merged neuron: summed expression, summed/mean cell area,
    summed counts, mean warped coordinates, majority branchlabel, and the section /
    cell-id / obs-position lists recorded in *_list columns;
  * every unmatched cell -> a singleton (is_merged=False, chain_length=1); its
    cell_class is neuron iff its final_annot is in --neuron-types, else non-neuron.

obs columns: cell_class, is_merged, chain_length, n_sections, final_annot,
branchlabel, spot_class, warp_x/y/z, total_cell_area, mean_cell_area,
total_counts, sampleid, sampleid_list, cell_id_list, block_pos_list.
obsm: spatial_warp (mean warp_x/y/z); spatial (mean raw coords) if the input had it.

Required input obs: sampleid, cell_id, final_annot, warp_x, warp_y, warp_z.
Optional (defaulted if absent): branchlabel, spot_class, total_counts, cell_area,
and obsm['spatial'].
"""
import argparse
import gzip
import numpy as np
import pandas as pd
import scipy.sparse as sp
import anndata as ad


def _col(obs, name, default, dtype=None):
    if name in obs.columns:
        v = obs[name].to_numpy()
        return v.astype(dtype) if dtype else v
    return np.full(len(obs), default)


def read_chains(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as fh:
        return [sorted(int(x) for x in line.split(',')) for line in fh if line.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('-i', '--input', required=True, help='warped_allcells.h5ad')
    ap.add_argument('-c', '--chains', required=True, help='chains tsv(.gz) from step 02')
    ap.add_argument('-o', '--output', required=True, help='merged h5ad')
    ap.add_argument('--neuron-types', required=True, help='one final_annot per line')
    a = ap.parse_args()

    neuron_types = set(l.strip() for l in open(a.neuron_types) if l.strip())
    A = ad.read_h5ad(a.input)
    A.obs = A.obs.reset_index(drop=True)
    chains = read_chains(a.chains)

    n = A.n_obs
    W = A.obs[['warp_x', 'warp_y']].to_numpy().astype(float)
    Z = A.obs['warp_z'].to_numpy().astype(float)
    samp = A.obs['sampleid'].astype(str).to_numpy()
    cid = A.obs['cell_id'].astype(str).to_numpy()
    annot = A.obs['final_annot'].astype(str).to_numpy()
    branch = _col(A.obs, 'branchlabel', 'NA').astype(str)
    spotc = _col(A.obs, 'spot_class', 'NA').astype(str)
    tc = _col(A.obs, 'total_counts', 0.0, float)
    area = _col(A.obs, 'cell_area', 0.0, float)
    is_neuron = np.isin(annot, list(neuron_types))
    has_raw = 'spatial' in A.obsm
    raw = A.obsm['spatial'].astype(float) if has_raw else None
    X = A.X.tocsr()

    in_chain = np.zeros(n, bool)
    for ch in chains:
        for c in ch:
            in_chain[c] = True

    rows = []; Xparts = []; sp_raw = []; sp_warp = []

    for ch in chains:
        frag = np.array(ch)
        Xparts.append(X[frag].sum(0))
        bl = pd.Series(branch[frag]).mode()
        bl = bl.iloc[0] if len(bl) else 'NA'
        rep = frag[np.argmax(tc[frag])] if tc[frag].any() else frag[0]
        rows.append(dict(
            cell_class='neuron', is_merged=True, chain_length=len(frag),
            n_sections=len(set(samp[frag])), final_annot=annot[frag[0]],
            branchlabel=bl, spot_class='merged_neuron',
            warp_x=W[frag, 0].mean(), warp_y=W[frag, 1].mean(), warp_z=Z[frag].mean(),
            total_cell_area=area[frag].sum(), mean_cell_area=area[frag].mean(),
            total_counts=tc[frag].sum(), sampleid=samp[rep],
            sampleid_list=','.join(samp[frag]), cell_id_list=','.join(cid[frag]),
            block_pos_list=','.join(map(str, frag.tolist()))))
        sp_warp.append([W[frag, 0].mean(), W[frag, 1].mean(), Z[frag].mean()])
        if has_raw:
            sp_raw.append(raw[frag].mean(0))

    singletons = np.where(~in_chain)[0]
    for p in singletons:
        Xparts.append(X[p])
        rows.append(dict(
            cell_class='neuron' if is_neuron[p] else 'non-neuron', is_merged=False,
            chain_length=1, n_sections=1, final_annot=annot[p], branchlabel=branch[p],
            spot_class=spotc[p], warp_x=W[p, 0], warp_y=W[p, 1], warp_z=Z[p],
            total_cell_area=area[p], mean_cell_area=area[p], total_counts=tc[p],
            sampleid=samp[p], sampleid_list=samp[p], cell_id_list=cid[p],
            block_pos_list=str(p)))
        sp_warp.append([W[p, 0], W[p, 1], Z[p]])
        if has_raw:
            sp_raw.append(raw[p])

    obs = pd.DataFrame(rows)
    obs.index = (['merged_%d' % i for i in range(len(chains))] +
                 ['cell_%d' % i for i in range(len(singletons))])
    Xout = sp.vstack([x if sp.issparse(x) else sp.csr_matrix(x) for x in Xparts]).tocsr()
    out = ad.AnnData(X=Xout, obs=obs, var=A.var.copy())
    out.obsm['spatial_warp'] = np.array(sp_warp)
    if has_raw:
        out.obsm['spatial'] = np.array(sp_raw)
    for c in ['cell_class', 'final_annot', 'branchlabel', 'spot_class', 'sampleid']:
        out.obs[c] = out.obs[c].astype('category')
    out.write(a.output)

    neu = int((out.obs.cell_class == 'neuron').sum())
    nn = int((out.obs.cell_class == 'non-neuron').sum())
    print(f'  wrote {a.output}: {out.shape} | neurons={neu} (merged {len(chains)}) | '
          f'non-neurons={nn} | sections={out.obs["sampleid"].nunique()}')


if __name__ == '__main__':
    main()
