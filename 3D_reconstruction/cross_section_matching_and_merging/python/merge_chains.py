#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:
"""DP merge (step 02): candidate links -> merged multi-section chains.

Read the edge table from step 01 and, independently per cell type:
  1. build linear threads (a maximal a->b->c... path from the pairwise links);
  2. for each thread, dynamic-programming pick a non-overlapping set of at most
     (--max-sections - 1) CONSECUTIVE links maximising sum(--radius - dist), so a
     merged cell never spans more than --max-sections sections and closer matches
     are preferred;
  3. take connected components of the selected links -- these are the chains.

Output: a gzipped TSV, one merged chain per line, as a comma-separated list of
0-based obs positions (chain length >= 2). Singletons are NOT listed here (they
are handled in step 03).
"""
import argparse
import numpy as np
import pandas as pd
from collections import defaultdict


def build_threads(edges):
    """edges: iterable of (a, b, dist). Chain each cell to its unique successor
    (a->b) and predecessor (b->a) into maximal linear threads. Returns a list of
    (cells, dists) where cells is the ordered path and dists the between-link
    distances."""
    nxt = {}; prv = {}
    for a, b, d in edges:
        nxt[a] = (b, d); prv[b] = (a, d)
    threads = []
    for start in nxt:
        if start in prv:      # not a thread head
            continue
        chain = [start]; dists = []; cur = start
        while cur in nxt:
            nx, d = nxt[cur]; chain.append(nx); dists.append(d); cur = nx
        threads.append((chain, dists))
    return threads


def dp_merge(threads, radius, max_sections):
    """Per thread, choose links (edges between consecutive cells) so that no run of
    kept links exceeds (max_sections - 1) consecutive links, maximising the summed
    weight radius - dist. Returns the set of selected (cell_i, cell_{i+1}) links."""
    max_edges = max_sections - 1
    selected = set()
    for cells, dists in threads:
        m = len(dists)
        if m == 0:
            continue
        w = [radius - d for d in dists]
        # dp[i][c]: best score using first i links, with c consecutive links kept
        # up to i (c resets to 0 whenever a link is skipped).
        dp = [[-1e18] * (max_edges + 1) for _ in range(m + 1)]
        par = [[None] * (max_edges + 1) for _ in range(m + 1)]
        dp[0][0] = 0.0
        for i in range(m):
            for c in range(max_edges + 1):
                if dp[i][c] == -1e18:
                    continue
                if dp[i][c] > dp[i + 1][0]:                       # skip link i
                    dp[i + 1][0] = dp[i][c]; par[i + 1][0] = (i, c, 's')
                if c < max_edges:                                # take link i
                    v = dp[i][c] + w[i]
                    if v > dp[i + 1][c + 1]:
                        dp[i + 1][c + 1] = v; par[i + 1][c + 1] = (i, c, 't')
        bc = int(np.argmax(dp[m])); acts = []; i, c = m, bc
        while par[i][c]:
            pi, pc, act = par[i][c]; acts.append(act); i, c = pi, pc
        for ei, act in enumerate(acts[::-1]):
            if act == 't':
                selected.add((cells[ei], cells[ei + 1]))
    return selected


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('-e', '--edges', required=True, help='edges tsv(.gz) from step 01')
    ap.add_argument('-o', '--output', required=True, help='chains tsv(.gz)')
    ap.add_argument('--radius', type=float, default=30.0)
    ap.add_argument('--max-sections', type=int, default=3)
    a = ap.parse_args()

    edf = pd.read_csv(a.edges, sep='\t')
    selected = set()
    if len(edf):
        for ct, g in edf.groupby('ct', observed=True):
            selected |= dp_merge(build_threads(list(zip(g['a'], g['b'], g['dist']))),
                                 a.radius, a.max_sections)

    adj = defaultdict(list)
    for u, v in selected:
        adj[u].append(v); adj[v].append(u)
    seen = set(); chains = []
    for node in adj:
        if node in seen:
            continue
        stack = [node]; comp = []; seen.add(node)
        while stack:
            x = stack.pop(); comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        chains.append(sorted(comp))

    with __import__('gzip').open(a.output, 'wt') if a.output.endswith('.gz') else open(a.output, 'w') as fh:
        for ch in chains:
            fh.write(','.join(map(str, ch)) + '\n')
    print(f'  DP-selected links: {len(selected)} | merged chains (len>=2): {len(chains)}')
    print(f'  wrote {a.output}')


if __name__ == '__main__':
    main()
