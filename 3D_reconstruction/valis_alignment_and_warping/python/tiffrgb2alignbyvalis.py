#!/usr/bin/env python3
# vim: set noexpandtab tabstop=2 shiftwidth=2 softtabstop=-1 fileencoding=utf-8:
# Register a serial section image stack with Valis, in the order the files are given.
# Writes the aligned images, the registration error summary and the registrar used for warping.

import argparse
from pathlib import Path
from valis import registration

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('-d', '--outdir', default='.')
parser.add_argument('-b', '--bname', required=True)
parser.add_argument('--maxprocessdim', type=int, default=1024, help='Max width or height for image processing.')
parser.add_argument('--maxnonrigiddim', type=int, default=1024, help='Max width or height for non-rigid registration.')
parser.add_argument('-c', '--crop', default='overlap', choices=['all', 'overlap', 'reference'])
parser.add_argument('-s', '--sortimage', action='store_true', help='Let Valis order the images instead of keeping the input order.')
parser.add_argument('-n', '--fname', action='append', required=True, help='Slide name of each input image, repeatable and in input order.')
parser.add_argument('infile', nargs='+')
args=parser.parse_args()

outdir=args.outdir
bname=args.bname
fname=args.fname
infile=args.infile
crop=args.crop
Path(outdir).mkdir(parents=True, exist_ok=True)

if len(fname)!=len(infile):
	raise ValueError(f"{len(fname)} names for {len(infile)} images.")

# Link infile and create a srcdir
srcdir=f"{outdir}/{bname}_src"
Path(srcdir).mkdir(parents=True, exist_ok=True)
srcfile=[]
for file, name in zip(infile, fname):
	dest=Path(srcdir) / f"{name}.tif"
	if not dest.exists():
		dest.symlink_to(Path(file).resolve())
	srcfile+=[str(dest)]

# Define Valis object
registrar = registration.Valis(
	name=bname,
	src_dir=srcdir,
	dst_dir=f"{outdir}/{bname}_work",
	img_list=dict(zip(srcfile, fname)),
	max_processed_image_dim_px=args.maxprocessdim,
	max_non_rigid_registration_dim_px=args.maxnonrigiddim,
	imgs_ordered=not args.sortimage,
	image_type='brightfield',
	)

# Run the registration
rigid_registrar, non_rigid_registrar, error_df = registrar.register()

# Save all registered slides as ome.tiff
registrar.warp_and_save_slides(f"{outdir}/{bname}_align", crop=crop)

error_df.to_csv(f"{outdir}/{bname}_summary.txt.gz", sep='\t', index=False)

# Kill the JVM
registration.kill_jvm()
