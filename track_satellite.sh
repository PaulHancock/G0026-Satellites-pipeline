#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=gpuq
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --mem=32gb
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/track.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/track.sh.e%A

aprun='aprun -n 1 -d 8 -b'

cd /astro/mwasci/phancock/G0026
$aprun python track_satellite.py > tracking.dat
