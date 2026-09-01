# Cross-section cell matching and merging

Reconstruct 3D cells from the aligned, warped serial sections by **matching the
same cell across adjacent sections** and **merging** the matched fragments into
single multi-section cells. This is the step that follows
`3D_reconstruction/valis_alignment_and_warping`.

Because 12&nbsp;µm sections oversample cells along z, one physical cell often appears
in 2–3 consecutive sections. Matching links those fragments; merging collapses each
linked chain into one cell (summed expression, mean warped position), while every
unmatched cell is carried through unchanged.

## Input

Per side, the all-cell 3D object produced by the upstream module (its step 17):

```
valis_alignment_and_warping/result/17_h5ad_allcells/mouse_${side}TG_warped_allcells.h5ad
```

Data is **not** committed. Point `WARPEDDIR` at the directory holding these files
(or drop / symlink them into `input/`). If a data release provides the
`mouse_${side}TG_warped_allcells.h5ad` files directly, use those; otherwise run the
`valis_alignment_and_warping` module first and point `WARPEDDIR` at its
`result/17_h5ad_allcells/`.

Required `obs` columns: `sampleid`, `cell_id`, `final_annot`, `warp_x`, `warp_y`,
`warp_z`. Used if present (defaulted otherwise): `branchlabel`, `spot_class`,
`total_counts`, `cell_area`, and `obsm['spatial']` (raw coordinates).

## Steps

| step | script | in → out |
|------|--------|----------|
| 01 | `01_match_sections.sh` → `python/match_sections.py` | `warped_allcells.h5ad` → `result/01_match_edges/mouse_${side}TG_match_edges.tsv.gz` |
| 02 | `02_merge_chains.sh` → `python/merge_chains.py` | edges → `result/02_merge_chains/mouse_${side}TG_chains.tsv.gz` |
| 03 | `03_assemble_merged_h5ad.sh` → `python/assemble_merged_h5ad.py` | h5ad + chains → `result/03_h5ad_merged/mouse_${side}TG_allcells_merged.h5ad` |

**01 — match.** For each adjacent section pair (ordered by `warp_z`, restricted to
the neuron block = sections with more than `MINNEURONS` neurons), among neurons of
the same `final_annot`: mutual-best-neighbour within `RADIUS` → crossover removal
(anchors) → thin-plate-spline warp of A onto B fit on the anchors → mutual-best-
neighbour again on the warped A, keeping a link if it is an anchor or its warped
source is within `TPSTHRESH` of an anchor and its distance ≤ `DISTFILTER`.

**02 — merge.** Per cell type, order the links into linear threads and, by dynamic
programming, keep a non-overlapping set of at most `MAXSECTIONS − 1` consecutive
links maximising `Σ(RADIUS − distance)`; connected components of the kept links are
the chains (length ≥ 2).

**03 — assemble.** Collapse each chain into one merged neuron; carry every unmatched
cell through as a singleton.

## Output

Per side, `mouse_${side}TG_allcells_merged.h5ad`, with `obs`:
`cell_class, is_merged, chain_length, n_sections, final_annot, branchlabel,
spot_class, warp_x, warp_y, warp_z, total_cell_area, mean_cell_area, total_counts,
sampleid, sampleid_list, cell_id_list, block_pos_list`, and `obsm['spatial_warp']`
(mean warped x/y/z; `obsm['spatial']` too if the input carried raw coordinates).
`*_list` columns record, comma-separated, the constituent sections / cell ids /
input obs-positions of each merged cell (singletons list themselves).

## Parameters (`config.sh`)

| var | default | meaning |
|-----|---------|---------|
| `RADIUS` | 30 | neighbour search radius (µm) for matching |
| `TPSTHRESH` | 50 | max distance (µm) of a warped source to an anchor |
| `DISTFILTER` | 20 | max accepted link distance (µm) after TPS |
| `MAXSECTIONS` | 3 | max sections a merged cell may span |
| `MINNEURONS` | 100 | a section joins the matching block only above this |
| `TPSSMOOTH` | 0.1 | thin-plate-spline smoothing |

## Run

```bash
export WARPEDDIR=/path/to/17_h5ad_allcells      # holds mouse_{left,right}TG_warped_allcells.h5ad
bash run_all.sh                                 # or run 01_, 02_, 03_ in order
```

Requires Python ≥ 3.10 with `anndata`, `numpy`, `pandas`, `scipy`.
