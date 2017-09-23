import astropy
from astropy.io import fits
import numpy as np
import sys

try:
    obsid = int(sys.argv[-1])
except ValueError as e:
    print "expecting obsid, found ",sys.argv[-1]
    sys.exit()

print "working on obsid", obsid

# TODO: set this via command line
nfreqs = 768
ntimes = 232

# Read the freq cubes and combine into a single massive file
base = '{0:d}-sm-'.format(obsid)
inbase = base + 't{0:04d}-freq-cube.fits'
outname = base + '3dcube.fits'

ref = fits.open(inbase.format(0))
ymin,ymax = 122, 222
xmin,xmax = 136, 216

data = np.empty((ntimes,nfreqs,ymax-ymin,xmax-xmin), dtype=np.float32)

for t in range(ntimes):
    # read freq zero file to act as a reference HDU
    fname = inbase.format(t)
    print fname
    data[t,:,:,:] = np.float32(fits.getdata(fname)[0,:,ymin:ymax,xmin:xmax])


ref[0].data = data

ref[0].header['CRPIX1'] -= xmin
ref[0].header['CRPIX2'] -= ymin

ref[0].header['CTYPE4'] = 'time'
ref[0].header['CRPIX4'] = 1
ref[0].header['CRVAL4'] = obsid
ref[0].header['CDELT4'] = 1
ref[0].header['CUNIT4'] = 'sec'

ref.writeto(outname)

