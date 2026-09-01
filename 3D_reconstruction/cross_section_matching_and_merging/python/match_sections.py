#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:
"""Cross-section neuron matching (step 01).

For each pair of adjacent serial sections (ordered by warp_z, restricted to the
neuron block -- sections carrying more than --min-neurons neurons), find
candidate same-cell links between neurons of the SAME final_annot:

  1. mutual best neighbour (MBN) within --radius microns                -> raw matches
  2. crossover removal (drop geometrically crossing links)              -> anchor matches
  3. thin-plate-spline (TPS) warp of section A onto B, fit on anchors
  4. MBN again on the TPS-warped A; keep a link if it is an anchor, or its warped
     source lies within --tps-thresh of an anchor source, and its link distance
     is <= --dist-filter                                                -> final edges

Output: a gzipped TSV with columns a, b, dist, ct, where a/b are 0-based row
positions in the input h5ad's obs (order preserved by reset_index) and ct is the
final_annot of a. These positions are consumed by 02 (merge_chains) and 03
(assemble_merged_h5ad), which re-read the same h5ad in the same order.
"""
import argparse
import numpy as np
import pandas as pd
import anndata as ad
from scipy.spatial import cKDTree
from scipy.interpolate import RBFInterpolator


def mbn(ca, cb, ta, tb, ia, ib, r):
    """Mutual-best-neighbour matches within the same cell type, radius r.
    Returns rows (a_row, b_row, a_idx, b_idx, dist) where *_row index into ca/cb
    and *_idx are the caller-supplied global ids ia/ib."""
    tb_ = cKDTree(cb); ta_ = cKDTree(ca)
    bfa = np.full(len(ca), -1); bda = np.full(len(ca), np.inf)
    for i, nb in enumerate(tb_.query_ball_point(ca, r)):
        if not nb:
            continue
        nb = np.array(nb); same = nb[tb[nb] == ta[i]]
        if len(same) == 0:
            continue
        d = np.linalg.norm(cb[same] - ca[i], axis=1); k = np.argmin(d)
        bfa[i] = same[k]; bda[i] = d[k]
    bfb = np.full(len(cb), -1)
    for j, nb in enumerate(ta_.query_ball_point(cb, r)):
        if not nb:
            continue
        nb = np.array(nb); same = nb[ta[nb] == tb[j]]
        if len(same) == 0:
            continue
        bfb[j] = same[np.argmin(np.linalg.norm(ca[same] - cb[j], axis=1))]
    return pd.DataFrame(
        [(i, j, ia[i], ib[j], bda[i]) for i, j in enumerate(bfa) if j >= 0 and bfb[j] == i],
        columns=['a_row', 'b_row', 'a_idx', 'b_idx', 'dist'])


def _seg(p1, p2, q1, q2, e=1e-9):
    """True if segment p1-p2 properly crosses segment q1-q2."""
    def cc(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1 = cc(q1, q2, p1); d2 = cc(q1, q2, p2); d3 = cc(p1, p2, q1); d4 = cc(p1, p2, q2)
    return (((d1 > e and d2 < -e) or (d1 < -e and d2 > e)) and
            ((d3 > e and d4 < -e) or (d3 < -e and d4 > e)))


def crem(ca, cb, m):
    """Crossover removal: iteratively drop the match involved in the most
    crossings (ties broken by the longer link) until no links cross."""
    if len(m) == 0:
        return m
    m = m.reset_index(drop=True)

    def crossings(mm):
        if len(mm) < 2:
            return []
        ap = ca[mm['a_row'].values]; bp = cb[mm['b_row'].values]
        L = np.linalg.norm(ap - bp, axis=1).max()
        t = cKDTree((ap + bp) / 2); cd = t.query_ball_tree(t, L)
        return [(i, j) for i in range(len(mm)) for j in cd[i]
                if j > i and _seg(ap[i], bp[i], ap[j], bp[j])]

    keep = np.ones(len(m), bool)
    while True:
        si = np.where(keep)[0]
        if len(si) < 2:
            break
        sub = m.iloc[si].reset_index(drop=True); cs = crossings(sub)
        if not cs:
            break
        v = np.zeros(len(sub))
        for i, j in cs:
            v[i if sub['dist'].iat[i] >= sub['dist'].iat[j] else j] += 1
        keep[si[int(np.argmax(v))]] = False
    return m[keep].reset_index(drop=True)


def tps(src, dst, pts, smoothing):
    """Thin-plate-spline map fit on src->dst, applied to pts (identity if <3 anchors)."""
    if len(src) < 3:
        return pts.copy()
    return RBFInterpolator(src, dst, kernel='thin_plate_spline', smoothing=smoothing)(pts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('-i', '--input', required=True, help='warped_allcells.h5ad')
    ap.add_argument('-o', '--output', required=True, help='edges tsv(.gz)')
    ap.add_argument('--neuron-types', required=True, help='one final_annot per line')
    ap.add_argument('--radius', type=float, default=30.0)
    ap.add_argument('--tps-thresh', type=float, default=50.0)
    ap.add_argument('--dist-filter', type=float, default=20.0)
    ap.add_argument('--min-neurons', type=int, default=100)
    ap.add_argument('--tps-smooth', type=float, default=0.1)
    a = ap.parse_args()

    neuron_types = set(l.strip() for l in open(a.neuron_types) if l.strip())
    A = ad.read_h5ad(a.input)
    A.obs = A.obs.reset_index(drop=True); A.obs['pos'] = np.arange(A.n_obs)
    is_neuron = A.obs['final_annot'].isin(neuron_types).values
    W = A.obs[['warp_x', 'warp_y']].values.astype(float)

    nps = (A.obs.assign(n=is_neuron)
           .groupby('sampleid', observed=True)
           .agg(z=('warp_z', 'first'), neur=('n', 'sum')).sort_values('z'))
    block_secs = list(nps[nps['neur'] > a.min_neurons].index)
    sord = nps.loc[block_secs].sort_values('z').index.tolist()
    print(f'  total: {A.n_obs:,} cells, {A.obs["sampleid"].nunique()} sections | '
          f'neuron block: {len(sord)} sections')
    ncell = {s: A.obs[(A.obs['sampleid'] == s) & is_neuron]
             [['pos', 'warp_x', 'warp_y', 'final_annot']].reset_index(drop=True) for s in sord}

    anchor_set = set(); final_edges = []
    for k in range(len(sord) - 1):
        da = ncell[sord[k]]; db = ncell[sord[k + 1]]
        ca = da[['warp_x', 'warp_y']].values; cb = db[['warp_x', 'warp_y']].values
        ta = da['final_annot'].values; tb = db['final_annot'].values
        ia = da['pos'].values; ib = db['pos'].values

        m_anch = crem(ca, cb, mbn(ca, cb, ta, tb, ia, ib, a.radius))
        for _, r in m_anch.iterrows():
            anchor_set.add((int(r['a_idx']), int(r['b_idx'])))

        wa = (tps(ca[m_anch['a_row'].values], cb[m_anch['b_row'].values], ca, a.tps_smooth)
              if len(m_anch) >= 3 else ca.copy())
        m_post = mbn(wa, cb, ta, tb, ia, ib, a.radius)
        anchset_k = set(zip(m_anch['a_idx'], m_anch['b_idx']))
        tr = cKDTree(wa[m_anch['a_row'].values]) if len(m_anch) >= 1 else None
        for _, r in m_post.iterrows():
            aa, bb = int(r['a_idx']), int(r['b_idx'])
            isa = (aa, bb) in anchset_k
            keep = True if isa else (tr.query(wa[int(r['a_row'])], k=1)[0] <= a.tps_thresh
                                     if tr is not None else False)
            if keep and r['dist'] <= a.dist_filter:
                final_edges.append((aa, bb, float(r['dist'])))

    final_set = set((aa, bb) for aa, bb, _ in final_edges)
    added = final_set - anchor_set; deleted = anchor_set - final_set
    print('  --- TPS match-diff statistics ---')
    print(f'    pre-TPS anchors (warp_xy MBN + crossover): {len(anchor_set)}')
    print(f'    final merge edges (after TPS + dist-filter): {len(final_set)}')
    print(f'    NEW pairs found by TPS:   +{len(added)}')
    print(f'    pairs DELETED after TPS:  -{len(deleted)}')
    print(f'    net change: {len(final_set) - len(anchor_set):+d}')

    edf = pd.DataFrame(final_edges, columns=['a', 'b', 'dist'])
    edf['ct'] = A.obs['final_annot'].values[edf['a'].values] if len(edf) else pd.Series(dtype=str)
    edf.to_csv(a.output, sep='\t', index=False)
    print(f'  wrote {a.output}: {len(edf)} edges')


if __name__ == '__main__':
    main()
