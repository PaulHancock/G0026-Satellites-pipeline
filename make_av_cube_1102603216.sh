#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=workq
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/1102603216_av_cube.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/1102603216_av_cube.sh.e%A

module load mpi4py

aprun='aprun -n 20 -d 1 -b'

cd /astro/mwasci/phancock/G0026/flagging
$aprun python ../bin/make_mfs.py 1102603216
cd ../noflagging
$aprun python ../bin/make_mfs.py 1102603216
