# Post-Xenium Visium HD analysis

Transcriptome-wide Visium HD profiling of TG sections that were already run on Xenium. The Xenium
cell boundaries of each section are imported into Space Ranger as a custom segmentation, and the
2 µm bins are then aggregated back into those same cells, so the Visium HD and Xenium measurements
share one set of cell identities.

```
Xenium stacked morphology image ─ 01 inverted RGB image ─┐
Xenium imported segmentation ─ 02 cell boundaries GeoJSON ─ 03 µm → pixel ─┤
Visium HD FASTQ + CytAssist image ───────────────────────┴─ 04 spaceranger count
   └─ 05 SpatialData zarr ─ 06 binned h5ad ─ 07 aggregate 2 µm bins into cells
        └─ 08 filter empty cells/genes ─ 09 attach Xenium annotations
```

## Steps

| Script | Code | Key parameters |
| --- | --- | --- |
| `01_xenium_rgb_image.sh` | `python/tiffchannel2rgb.py` | pseudo-colour the 4 Xenium channels, invert to a brightfield-like RGB |
| `02_xenium_cell_boundaries_geojson.sh` | `python/xeniumcellboundaries2geojson.py` | `cell_boundaries.parquet` → GeoJSON, feature id = Xenium `cell_id`, microns |
| `03_geojson_micron_to_pixel.sh` | `python/geojson2xyscale.py` | scale x and y by 1/0.2125 = 4.70588… |
| `04_spaceranger_count.sh` | `spaceranger count` | `--image` = inverted RGB, `--cytaimage`, `--custom-segmentation-file`, `--nucleus-expansion-distance-micron 0`, `--custom-bin-size 4`, `--create-bam false` |
| `05_visiumhd_to_zarr.sh` | `python/spatialdataiovisiumhd2zarr.py` | `spatialdata_io.visium_hd`, all images, filtered counts, bins as squares |
| `06_zarr_to_bin_h5ad.sh` | `python/spatialdatazarr2tablesh5ad.py` | one `.h5ad` per bin size, plus obs/var tables |
| `07_aggregate_bins_to_cells.sh` | `python/visiumhdh5adsegpolygon2aggregateh5ad.py` | `square_002um` bins summed into the polygons of step 03, barcode = polygon `id` |
| `08_filter_cells.sh` | `python/scrnah5adfiltergenescellsbycounts.py` | drop cells and genes with fewer than 1 count |
| `09_attach_xenium_metadata.sh` | `python/h5adaddmetadatamerge.py` | left merge of the Xenium per-cell annotations on `cell_id`, missing cells labelled `Unassigned` |

Notes on the choices above:

- Space Ranger's `--darkimage` does not register the Xenium fluorescence stack against the CytAssist
  image, so the stack is pseudo-coloured and inverted (step 01) and passed as a brightfield `--image`.
- Xenium boundaries are stored in microns while Space Ranger expects the pixel space of the tissue
  image, hence the rescaling in step 03 by the Xenium pixel size of 0.2125 µm.
- The GeoJSON is written with `to_json()` so the FeatureCollection carries no extra `name`/`crs`
  keys, which Space Ranger rejects.
- In step 07 a bin contributes its counts to a polygon when its centre falls inside exactly one
  polygon; bins matching several polygons are dropped. `obs` keeps the polygon area, centroid and
  the number of assigned bins.

## Inputs

`samples.tsv`, tab-delimited, one row per section:

| Column | Description |
| --- | --- |
| `sampleid` | section name, shared with the Xenium pipeline |
| `fastqs` | comma-separated Visium HD R1,R2 FASTQ files |
| `cytaimage` | CytAssist image of that capture area |
| `xeniumdir` | `outs/` of the Xenium Ranger import for the same section (step 13 of `../Cell_segmentation_Xenium`) |
| `xeniumstack` | stacked 4-channel Xenium morphology OME-TIFF (step 01 of `../Cell_segmentation_Xenium`) |

Step 09 additionally reads `metadata/<sampleid>_metadata.txt.gz` (override with `METADATADIR`): a
headed, tab-delimited table with a `cell_id` column and the Xenium per-cell annotations to carry
over — cell type (`majorclass`, `final_annot`), TG side and branch labels, and niche assignment —
exported from the Xenium annotation and 3D reconstruction results. Sections without such a table
are skipped, and cells missing from it are labelled `Unassigned`.

The two sections profiled were `Round3_Slide05_Section06` and `Round3_Slide06_Section04`; raw and
processed data are deposited on the SPARC Data Portal (DOI 10.26275/h2w2-fgau).

## Usage

```bash
export OUTDIR=/path/to/result
export SPACERANGER_CONFIG=/path/to/spaceranger-4.1.0/sourceme.bash
export GENOME=/path/to/refdata-gex-mm10-2020-A
export PROBESET=/path/to/spaceranger-4.1.0/probe_sets/Visium_Mouse_Transcriptome_Probe_Set_v2.0_mm10-2020-A.csv
bash run_all.sh          # or run 01_*.sh ... 09_*.sh individually
```

Paths and parameters are collected in `config.sh`; every value there can be overridden from the
environment. Each script loops over the sections in `samples.tsv`. In the study every iteration was
submitted as an independent Slurm job; the resources requested per section were 120 GB for step 01,
80 GB for steps 02-03 and 05-09, and 10 cores / 70 GB for step 04.

## Software

- [Space Ranger 4.1.0](https://www.10xgenomics.com/support/software/space-ranger) with the Visium
  Mouse Transcriptome Probe Set v2.0 (mm10-2020-A) and the `refdata-gex-mm10-2020-A` reference.
- Python ≥3.10 with `numpy`, `pandas`, `pyarrow`, `tifffile`, `shapely`, `geopandas`, `scipy`,
  `anndata`, `scanpy`, `spatialdata`, `spatialdata-io` for the scripts in `python/`.

```bash
conda create -n spatialdata python=3.12
conda activate spatialdata
pip install numpy pandas pyarrow tifffile shapely geopandas scipy anndata scanpy spatialdata spatialdata-io
```

The Xenium side of the analysis — the segmentation whose boundaries are imported here — is in
[`../Cell_segmentation_Xenium`](../Cell_segmentation_Xenium).
