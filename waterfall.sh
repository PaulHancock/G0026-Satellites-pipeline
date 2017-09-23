#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=gpuq
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/waterfall.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/waterfall.sh.e%A

aprun='aprun -n 1 -d 8 -b'

cd /astro/mwasci/phancock/G0026/
$aprun python waterfall_plots.py
