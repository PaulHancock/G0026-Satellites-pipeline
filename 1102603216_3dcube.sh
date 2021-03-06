#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=gpuq
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --mem=32gb
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/1102603216_3dcube.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/1102603216_3dcube.sh.e%A

aprun='aprun -n 1 -d 8 -b'

cd /astro/mwasci/phancock/G0026/flagging
$aprun python ../bin/3dcube.py 1102603216
cd ../noflagging
$aprun python ../bin/3dcube.py 1102603216
