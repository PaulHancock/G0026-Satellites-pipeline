#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=gpuq
#SBATCH --time=00:05:00
#SBATCH --nodes=1
#SBATCH --mem=32gb
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/python_test.sh.o%A_%a
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/python_test.sh.e%A_%a

aprun='aprun -n 1 -d 8 -b'
set -x
cd /astro/mwasci/phancock/G0026/bin
date
echo "load modules and quit"
aprun -n 1 -d 8 -b python stupid_script.py
date
aprun -n 1 -d 8 python stupid_script.py
date
echo "open a small file and read it"
aprun -n 1 -d 8 -b  python python_load_file.py
date
aprun -n 1 -d 8  python python_load_file.py
date
