# Serial section alignment and coordinate warping

Registration of the 87 Xenium serial sections into a common frame, and transfer of every cell from
its own section coordinates into that frame. The left and the right trigeminal ganglion (TG) are
aligned separately: each section image is cut into its two ganglia, the sections of one ganglion are
registered as a stack with [Valis](https://github.com/MathOnco/valis), and the same registration is
then applied to the cell geometries, giving 3D coordinates for every cell.

```
Xenium bundle
├─ morphology stack ─ 01 RGB image ─ 02 cut into left/right TG ─ 03 Valis registration ─ 04 inverted aligned images
│                                       │                            └─ registrar
├─ cell metadata ─ 05 assign leftTG/rightTG by polygon ─ 09 cell ids and metadata per section
└─ 06 zarr ─ 07 shapes GeoJSON (µm) ─ 08 → pixels ─ 10 subset per TG ─ 11 warp with the registrar
                                                       └─ 12 add cell type ─ 13 → µm ─ 14 stack in z
                                                            └─ 15 add niche ─ 16 warp_x/y/z table
                                                                 └─ 17 attach to expression ─ 18 neurons only
```

## Steps

| Script | Code | Key parameters |
| --- | --- | --- |
| `01_section_rgb_image.sh` | `python/tiffchannel2rgb.py` | pseudo-colour the 4 Xenium channels, invert to a brightfield-like RGB |
| `02_split_left_right_tg.sh` | `python/tiff2maskbypolygon.py` | keep one ganglion per image, white background |
| `03_valis_align.sh` | `python/tiffrgb2alignbyvalis.py` | rigid + non-rigid registration, `crop=overlap`, sections kept in the order of `sides.tsv` |
| `04_invert_aligned_images.sh` | `python/tiffcolor2invertintensity.py` | aligned images back to a dark background, for figures |
| `05_assign_tg_label.sh` | `python/xeniummetadata2addlabelbypolygon.py` | label each cell `leftTG`/`rightTG` by the polygons of step 02 |
| `06_xenium_to_zarr.sh` | `python/spatialdataioxenium2zarr.py` | Xenium bundle → SpatialData, cells also as circles |
| `07_zarr_to_shapes_geojson.sh` | `python/spatialdatazarr2shapesgeojson.py` | cell circles, cell boundaries, nucleus boundaries, in microns |
| `08_shapes_micron_to_pixel.sh` | `python/geojson2xyscale.py` | scale by 1/0.2125 = 4.70588…, the space the registration works in |
| `09_select_cells_per_side.sh` | `python/tsvfile2splitpdgroupby.py` | cell ids and metadata of each section, split by ganglion |
| `10_subset_shapes_per_side.sh` | `python/geojson2subsetbyproperty.py` | keep the shapes of that ganglion's cells |
| `11_warp_shapes_by_valis.sh` | `python/valisregistrar2warpgeojson.py` | `slide.warp_geojson(non_rigid=True, crop=overlap)` at full resolution |
| `12_add_annotation_property.sh` | `python/geojson2addpropertyby.py` | carry `final_annot` onto the warped shapes |
| `13_shapes_pixel_to_micron.sh` | `python/geojson2xyscale.py` | scale by 0.2125 |
| `14_stack_sections_in_z.sh` | `python/geojson2pointzstitch.py` | z = 0, 12, 24 … µm following the order of `sides.tsv` |
| `15_add_neighborhood_property.sh` | `python/geojson2addpropertycompositekey.py` | carry the niche label, matched on (section, cell), missing → `Unassigned` |
| `16_warped_coordinates_table.sh` | `python/geojsonpointexpand2pdcolumn.py` | point geometry → `warp_x`, `warp_y`, `warp_z` |
| `17_attach_warped_coordinates_to_h5ad.sh` | `python/h5adaddmetadatamergebycompositekey.py` | inner merge into the expression matrix on (`sampleid`, `cell_id`) |
| `18_subset_neurons.sh` | `python/scrnah5adsubsetbycelltype.py` | keep the 15 neuronal types of `neuron_types.txt` |

Notes on the choices above:

- Valis is given the sections already in serial order (`imgs_ordered=True`), so the row order of
  `sides.tsv` defines both the registration order and the z coordinate of step 14.
- The two ganglia of one section drift apart along the series, so they are registered as two
  independent stacks; a cell belongs to exactly one of them (step 05).
- The 17 sections of Round 1 and Round 2 carry both ganglia in one piece of tissue and were
  registered from the whole-section image (`image` column set to `whole`); the remaining sections use
  the masked single-ganglion image (`mask`).
- Coordinates make two round trips between microns and pixels: the registration works in image
  pixels, the deposited coordinates are microns.

## Inputs

`samples.tsv`, one row per section:

| Column | Description |
| --- | --- |
| `sampleid` | section name |
| `xeniumstack` | stacked 4-channel Xenium morphology OME-TIFF (step 01 of `../../Cell_segmentation_Xenium`) |
| `xeniumdir` | `outs/` of the Xenium Ranger import for that section (step 13 of `../../Cell_segmentation_Xenium`) |

`sides.tsv`, one row per section and ganglion, **in serial order within each side**:

| Column | Description |
| --- | --- |
| `side` | `left` or `right` |
| `sampleid` | section name |
| `polygon` | GeoJSON polygon of that ganglion in that section, drawn once per section |
| `image` | `mask` to register the masked ganglion, `whole` to register the whole-section image |

Sections missing from a side are simply left out of `sides.tsv`, which is how damaged tissue was
excluded from a registration.

Set in `config.sh` or the environment:

- `CELLMETA`: per-cell annotation table with `sampleid`, `cell_id`, `x`, `y` (microns) and `final_annot`
- `EXPRH5AD`: concatenated Xenium expression matrix of all sections, `obs` carrying `sampleid` and `cell_id`
- `NEIGHBORHOOD` (optional): `sampleid`, `cell_id`, `neighborhood`; step 15 is skipped when absent

## Outputs

Per ganglion, in `result/17_h5ad_allcells` and `result/18_h5ad_neuron`:

- `mouse_leftTG_warped_allcells.h5ad`, `mouse_rightTG_warped_allcells.h5ad`
- `mouse_leftTG_warped_neuron.h5ad`, `mouse_rightTG_warped_neuron.h5ad`

Each carries the Xenium expression matrix with `warp_x`, `warp_y`, `warp_z` in microns, the cell type
annotation and the niche label. These are the objects deposited on the SPARC Data Portal
(DOI 10.26275/h2w2-fgau) and the input to the later 3D reconstruction steps.

## Usage

```bash
conda activate valis        # environment with valis, spatialdata and scanpy
export OUTDIR=/path/to/result
export CELLMETA=/path/to/mouseTG_metadata.txt.gz
export EXPRH5AD=/path/to/mouseTG_expr.h5ad
bash run_all.sh             # or run 01_*.sh ... 18_*.sh individually
```

Paths and parameters are collected in `config.sh`; every value there can be overridden from the
environment. In the study each section (or each side, for steps 03 and 14) was submitted as an
independent Slurm job; the resources requested were 2 cores / 80 GB for the image and shape steps,
2 cores / 200-300 GB and up to three days for the two Valis registrations, 32 cores / 120 GB for
step 05, 2 cores / 20 GB for the warping, and 2 cores / 80 GB for the table and `.h5ad` steps.

## Notes on the code

The scripts in `python/` are the code that produced the deposited objects, rewritten only to take
their parameters on the command line instead of from the job wrappers used on the cluster. Two
things differ from the archive:

- Sections were renamed once during the project, and the cluster scripts carried a `sampleid_legacy`
  lookup to find the older file names. Here every file is named by `sampleid`, so the lookup is gone.
- `h5adaddmetadatamergebycompositekey.py` is a reimplementation, since that tool ships without its
  payload. It merges on the same composite key with the same merge type; unmatched **text** columns
  get the NA string, while unmatched numeric columns stay `NaN` so that `obs` remains writable.

## Software

- [Valis](https://github.com/MathOnco/valis) for the registration and for warping the geometries with
  the saved registrar.
- Python ≥3.10 with `numpy`, `pandas`, `pyarrow`, `tifffile`, `rasterio`, `shapely`, `geopandas`,
  `joblib`, `scipy`, `anndata`, `scanpy`, `spatialdata`, `spatialdata-io`.

```bash
conda create -n valis python=3.11
conda activate valis
pip install valis-wsi
pip install numpy pandas pyarrow tifffile rasterio shapely geopandas joblib scipy anndata scanpy spatialdata spatialdata-io
```

The segmentation that produced the cells warped here is in
[`../../Cell_segmentation_Xenium`](../../Cell_segmentation_Xenium).
