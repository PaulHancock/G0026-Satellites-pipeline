#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=gpuq
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --mem=32gb
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/1102604896_av_cube.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/1102604896_av_cube.sh.e%A

module load mpi4py

aprun='aprun -n 8 -d 1 -b'

cd /astro/mwasci/phancock/G0026/flagging
$aprun python ../bin/make_mfs.py 1102604896
cd ../noflagging
$aprun python ../bin/make_mfs.py 1102604896
