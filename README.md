# A three-dimensional spatial atlas of the mouse trigeminal ganglion

This repository contains code and analyses for the spatial atlas of the mouse trigeminal ganglion (TG). This study was conducted as part of the [Restoring Joint Health and Function to Reduce Pain (RE-JOIN) Consortium](https://sparc.science/about/consortia/re-join), an [NIH HEAL Initiative](https://www.nih.gov/heal) program.

## Experimental design

The left and right trigeminal ganglia (TGs) from one adult wild-type C57BL/6 mouse (8-week-old, male) were serially sectioned at a thickness of 12 μm along the dorsoventral axis. All 87 sections spanning both TGs were profiled using the 10x Genomics Xenium platform with a customized gene panel ([10x Genomics Mouse Brain panel](https://www.10xgenomics.com/products/xenium-v1-panel), 97 additional genes, and 3 reporter genes).

For each section, two-dimensional cell segmentation and cell-type annotation were performed to identify neuronal and non-neuronal cell populations. The annotated serial sections were subsequently spatially registered, and cellular and regional information was used to establish correspondence across sections and generate a common 3D spatial framework.


## Data modalities

The raw and processed datasets have been deposited in the SPARC Data Portal under DOI 10.26275/h2w2-fgau, and will be made publicly available upon publication.

- Xenium: 87 serial sections profiled using a customized gene panel
- Visium HD: post-Xenium transcriptome-wide spatial profiling of 2 selected Xenium slides (4 TG sections)
- 3D reconstruction: computational integration of serial Xenium sections into a common 3D coordinate framework


## System requirements
The pipeline is expected to run on standard Linux-based high-performance computing environments with R and Python installed. The full workflow was tested on Linux Rocky Linux 8.8 and above. No non-standard hardware required.
- R version: R 4.3.2 
- Python version: Python v3.10 and above


## Codes and pipelines
- Cell segmentation (2D) of the Xenium data
- Cell annotation
- 3D reconstruction
- Post-Xenium VisiumHD analysis
- Downstream analysis

### Versions of the software

scvi-tools: v1.2.0;
Scanpy: v1.10.3;
Space Ranger: ?;
Xenium Ranger: v3.1.0;
Seurat: v5.3.0;
Harmony: v1.2.3;
spacexr: v2.2.1;
Squidpy:  v1.6.2;


## Interactive Browsers

We are still working on it...

## Questions

If you have any questions, please submit an issue to this repository.
