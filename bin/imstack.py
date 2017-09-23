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
inbase = base + 't{0:04d}-{1:04d}-image.fits'

# create cubes of (freq,ra,dec)
outbase = base + 't{0:04d}-freq-cube.fits'
for t in range(rank, ntimes, size):
    # skip existing files
    outname = outbase.format(t)
    if os.path.exists(outname):
        print " (skipping)"
        continue

    # read freq zero file to act as a reference HDU
    fname = inbase.format(t, 0)
    ref = fits.open(fname)
    # create empty array
    data = np.empty((1, nfreqs, 320, 320))
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print " {0}".format(fname)
    # build up the data array one freq at a time
    for f in range(nfreqs):
        fname = inbase.format(t, f)
        data[0, f, :, :] = fits.getdata(fname)
    # convert to int32 and save
    ref[0].data = np.float32(data)
    ref.writeto(outname)
    print outname

# create cubes of (time,ra,dec)
outbase = base + 'f{0:04d}-time-cube.fits'
for f in range(rank, nfreqs, size):
    # skip existing files
    outname = outbase.format(f)
    if os.path.exists(outname):
        print " (skipping)"
        continue

    # read freq zero file to act as a reference HDU
    fname = inbase.format(0, f)
    ref = fits.open(fname)
    # create empty array
    data = np.empty((1, ntimes, 320, 320))
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print " {0}".format(fname)
    # build up the data array one freq at a time
    for t in range(ntimes):
        fname = inbase.format(t, f)
        data[0, t, :, :] = fits.getdata(fname)
    # update the header to be in units of time instead of frequency
    ref[0].header['CTYPE3'] = 'time'
    ref[0].header['CRPIX3'] = 1
    ref[0].header['CRVAL3'] = obsid
    ref[0].header['CDELT3'] = 0.5
    ref[0].header['CUNIT3'] = 'sec'
    # convert data to int32 and save
    ref[0].data = np.float32(data)
    ref.writeto(outname)
    print outname
