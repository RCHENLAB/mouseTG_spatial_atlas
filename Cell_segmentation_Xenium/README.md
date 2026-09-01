# Cell segmentation (2D) of the Xenium data

Two-dimensional cell segmentation of each Xenium serial section of the mouse trigeminal ganglion (TG).
Neurons and non-neurons differ by an order of magnitude in size, so they are segmented separately and
then harmonized into a single boundary set, which is re-quantified with Xenium Ranger.

```
morphology_focus (4 channels)
  └─ 01 stack ─ 02 intensity histogram ─ 03 background filter
       ├─ neurons:     05 island mask ─ 06 masked image ─ 07 Cellpose (Protein/RNA, d=180) ─ 08 GeoJSON
       └─ non-neurons: 09 Cellpose (Protein/DAPI, d=20) ─ 10 GeoJSON ─ 11 transcript-ratio filter
                                                    (04 marker transcripts feed step 11)
                                12 combine neuron + non-neuron boundaries
                                13 xeniumranger import-segmentation
```

## Channels

| Index | Channel | Xenium file | Background threshold |
| --- | --- | --- | --- |
| 0 | DAPI | morphology_focus_0000.ome.tif | 200 |
| 1 | CB (ATP1A1/CD45/E-Cadherin) | morphology_focus_0001.ome.tif | 1000 |
| 2 | RNA (18S) | morphology_focus_0002.ome.tif | 2000 |
| 3 | Protein (AlphaSMA/Vimentin) | morphology_focus_0003.ome.tif | 500 |

## Steps

| Script | Code | Key parameters |
| --- | --- | --- |
| `01_stack_morphology_channels.sh` | `python/xeniumtif2npstack.py` | stack channels 0-3 into one OME-TIFF |
| `02_channel_intensity_histogram.sh` | `python/xeniumfocustiff2intensityhist.py` | log10 intensity, 1000 breaks; used to pick thresholds |
| `03_filter_low_intensity.sh` | `python/xeniumfocustiff2filterbyintensity.py` | thresholds 200/1000/2000/500 |
| `04_marker_transcripts_to_csv.sh` | `python/xeniumtranscriptsparquet2csv.py` | marker sets in `markers.tsv`, level 0 (0.2125 µm/pixel) |
| `05_neuron_island_mask.sh` | `python/xeniumtif2islandgeojsonbycv2.py` | RNA channel, Otsu threshold after 11×11 Gaussian blur, closing kernel 11, dilation 5 |
| `06_neuron_mask_image.sh` | `python/xeniumfocustiff2maskbyislandimage.py` | mask threshold 127 |
| `07_neuron_cellpose.sh` | Sopa Snakemake workflow | `yaml/neuron/*.yaml`; cyto3, diameter 180, cellprob 0, flow 0.95 |
| `08_neuron_shapes_to_geojson.sh` | `python/sopashapesparquet2geojson.py` | `cellpose_boundaries/shapes.parquet` → GeoJSON, pixel units |
| `09_nonneuron_cellpose.sh` | Sopa Snakemake workflow | `yaml/nonneuron/*.yaml`; cyto3, diameter 20, cellprob -2, flow 0.95 |
| `10_nonneuron_shapes_to_geojson.sh` | `python/sopashapesparquet2geojson.py` | as step 08 |
| `11_nonneuron_filter_by_transcript_ratio.sh` | `python/xeniumsubsetpolygonbytranscriptratio.py` | keep polygons with ≥10% non-neuron marker transcripts (`glianonneuron12` vs `neuron3`) |
| `12_combine_neuron_nonneuron.sh` | `python/xeniumcombinetgsegmentations.py` | subtract non-neuron polygons from overlapping neuron polygons; drop neuron polygons contained in a non-neuron polygon |
| `13_xeniumranger_import_segmentation.sh` | `xeniumranger import-segmentation` | nuclei = non-neuron boundaries (step 10), cells = combined boundaries (step 12), expansion 0 µm, pixel units |

Both a Protein- and a CB-based Cellpose configuration were run for each branch. The final boundaries
use `protein_rna_180_t0` (neurons) and `protein_dapi_20_tm2` (non-neurons); the `cb_*` configurations
were kept for comparison and are not used downstream.

Step 13 writes one Xenium bundle per section under `result/13_xeniumranger_import/<sampleid>/outs`,
which is the input to cell-type annotation and 3D reconstruction.

## Inputs

- `samples.tsv`: tab-delimited, `sampleid` and the path to the Xenium output bundle of that section.
  Replace the template rows with the 87 serial sections deposited on the SPARC Data Portal
  (DOI 10.26275/h2w2-fgau).
- `markers.tsv`: marker sets used to score polygons in step 11.
- `yaml/`: Cellpose/Sopa segmentation configurations.
- `python/`: the image-processing and geometry code called by the shell scripts. Each script is
  standalone and takes its parameters on the command line (`-h` for usage).

## Usage

```bash
conda activate sopa      # environment with sopa, cellpose and snakemake
export OUTDIR=/path/to/result
export SOPA_WORKFLOW=/path/to/sopa/workflow
export XENIUMRANGER_CONFIG=/path/to/xeniumranger-3.1.0/xeniumranger-xenium3.1/sourceme.bash
bash run_all.sh          # or run 01_*.sh ... 13_*.sh individually
```

Paths and parameters are collected in `config.sh`; every value there can be overridden from the
environment.

Each script loops over the sections in `samples.tsv`. In the study every iteration was submitted as an
independent Slurm job; the resources requested per section were 80 GB for steps 01-02 and 08/10,
60 GB for step 03, 20 GB for step 04, 120 GB for steps 05 and 07/09, 40 GB for steps 11-12, and
4 cores / 60 GB / one GPU for step 13.

## Software

- [Xenium Ranger 3.1.0](https://www.10xgenomics.com/support/software/xenium-ranger) — step 13 calls
  `xeniumranger import-segmentation`. `XENIUMRANGER_CONFIG` points at the `sourceme.bash` of the
  installation, which is sourced before the call.
- [Sopa](https://github.com/gustaveroussy/sopa) — steps 07 and 09 run the Snakemake workflow shipped
  with Sopa (`workflow/` of a Sopa checkout, given by `SOPA_WORKFLOW`) with the configurations in
  `yaml/`. Cellpose provides the `cyto3` model.
- Python ≥3.10 with `numpy`, `pandas`, `pyarrow`, `tifffile`, `imagecodecs`, `opencv-python`,
  `shapely`, `geopandas`, `matplotlib` for the scripts in `python/`.

```bash
conda create -n sopa python=3.12
conda activate sopa
pip install 'sopa[cellpose]' snakemake
pip install numpy pandas pyarrow tifffile imagecodecs opencv-python shapely geopandas matplotlib
```
