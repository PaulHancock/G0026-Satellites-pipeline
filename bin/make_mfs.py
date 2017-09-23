import astropy
from astropy.io import fits
from astropy.wcs import WCS
from time import gmtime, strftime
import numpy as np
import os
import sys

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print "I am {0}/{1}".format(rank, size)

# Each instance should iterate through rank:nfreqs:size

try:
    obsid = int(sys.argv[-1])
except ValueError as e:
    print "expecting obsid, found ", sys.argv[-1]
    sys.exit()

print "working on obsid", obsid

# TODO: set this via command line
nfreqs = 768
ntimes = 232

base = '{0:d}-sm-'.format(obsid)

# merge cubes of (freq,ra,dec) into just (ra,dec)
inbase = base + 't{0:04d}-freq-cube.fits'
outbase = base + 't{0:04d}-freq-av.fits'
for t in range(rank, ntimes, size):
    # skip existing files
    outname = outbase.format(t)
    if os.path.exists(outname):
        print " (skipping)", outname
        continue

    # read freq zero file to act as a reference HDU
    fname = inbase.format(t)
    ref = fits.open(fname)
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print " {0}".format(fname)
    # average the data long the freq axis (TODO: skip the zero channels)
    data = np.average(ref[0].data, axis=1)
    # convert to int32 and save
    ref[0].data = np.float32(data)
    ref.writeto(outname)
    print outname

# create cubes of (time,ra,dec)
inbase = base + 'f{0:04d}-time-cube.fits'
outbase = base + 'f{0:04d}-time-av.fits'
for f in range(rank, nfreqs, size):
    # skip existing files
    outname = outbase.format(f)
    if os.path.exists(outname):
        print " (skipping)", outname
        continue

    # read freq zero file to act as a reference HDU
    fname = inbase.format(f)
    ref = fits.open(fname)
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print " {0}".format(fname)
    data = np.average(ref[0].data, axis=1)
    # convert data to int32 and save
    ref[0].data = np.float32(data)
    ref.writeto(outname)
    print outname
