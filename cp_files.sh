#!/bin/bash

#SBATCH --export=NONE
#SBATCH --account=mwasci
#SBATCH --clusters=zeus
#SBATCH --partition=copyq
#SBATCH --time=01:00:00

module load mpifileutils

# Edit this if your files are kept elsewhere
mydir=/astro/mwasci/phancock/G0026/satellite/

# Edit this to change which directory gets copied
dirtocopy=1102604896

# Edit this if you want to put your files somewhere else
destdir=/group/mwasci/phancock/temp

if [[ ! -d $destdir ]]
then
    mkdir $destdir ]]
fi

mpirun -np 12 dcp -p -d info ${mydir}/${dirtocopy} $destdir/$dirtocopy
