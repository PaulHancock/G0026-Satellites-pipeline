#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=gpuq
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --mem=32gb
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/make_images.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/make_images.sh.e%A

aprun='aprun -n 1 -d 8 -b'


datadir=/astro/mwasci/phancock/G0026

cd $datadir

obsnum=1102603216
ncpus=8

$aprun wsclean -name noflagging/${obsnum}-sm -size 320 320 \
               -weight briggs 0.5 -mfsweighting -scale 25.0amin \
               -pol I -niter 0 \
               -interval 0 232 -intervalsout 232 \
               -channelrange 0 768 -channelsout 768 \
               -maxuv-l 32 -minuv-l 0.03 -smallinversion -j ${ncpus} \
               satellite/${obsnum}_norfi.ms
