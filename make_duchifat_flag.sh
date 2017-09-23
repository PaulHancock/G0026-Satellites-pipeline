#!/bin/bash -l
#SBATCH --account=mwasci
#SBATCH --partition=workq
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --output=/astro/mwasci/phancock/G0026/queue/make_images.sh.o%A
#SBATCH --error=/astro/mwasci/phancock/G0026/queue/make_images.sh.e%A

# automatically set the right number of corse
# maybe leaving -d blank will do this ...
if [[ $SLURM_JOB_PARTITION -eq "gpuq" ]]
then
    cores=8
else #if [[ $SLURM_JOB_PARTITION -eq "workq" ]]
    cores=20
fi
aprun="aprun -n 1 -d ${cores} -b"


datadir=/astro/mwasci/phancock/G0026

cd $datadir

obsnum=1102603216

$aprun wsclean -name flagging/${obsnum}-sm -size 320 320 \
               -weight briggs 0.5 -mfsweighting -scale 25.0amin \
               -pol I -niter 0 \
               -interval 0 232 -intervalsout 232 \
               -channelrange 0 768 -channelsout 768 \
               -maxuv-l 32 -minuv-l 0.03 -smallinversion -j ${cores} \
               satellite/${obsnum}.ms
