#! python
# coding: utf-8

import astropy
from astropy.io import fits
from astropy.wcs import WCS
import ephem
import numpy as np
from matplotlib import pyplot
import os
import time
from datetime import datetime, timedelta

ntimes = 232
nfreqs = 768


def get_timestamp(gps_time):
    # J.F. Sebastian at http://stackoverflow.com/questions/33415475/how-to-get-current-date-and-time-from-gps-unsegment-time-in-python

    os.environ['TZ'] = 'right/UTC' # TAI scale with 1970-01-01 00:00:10 (TAI) epoch
    time.tzset()  # Unix
    gps_timestamp = gps_time  # 1102604896
    gps_epoch_as_gps = datetime(1980, 1, 6)
    # by definition
    gps_time_as_gps = gps_epoch_as_gps + timedelta(seconds=gps_timestamp)
    gps_time_as_tai = gps_time_as_gps + timedelta(seconds=19) # constant offset
    tai_epoch_as_tai = datetime(1970, 1, 1, 0, 0, 10)
    # by definition
    tai_timestamp = gps_time_as_tai - tai_epoch_as_tai
    tai_sec = tai_timestamp.seconds + tai_timestamp.days*3600*24
    dt = datetime.utcfromtimestamp(tai_sec)  # "right" timezone is in effect!
    return dt


def get_location_satellite(dt, satellite):
    # position of the observer
    mwa = ephem.Observer()
    mwa.lon = '116:40:14.93485'
    mwa.lat = '-26:42:11.94986'
    mwa.elevation = 377.827
    mwa.date = dt
    fname = '{0}.txt'.format(satellite)
    if not os.path.exists(fname):
        raise IOError("Cannot find {0} for reading".format(fname))
    # Read the TLE data for satellite.
    data = np.loadtxt(fname, dtype='string', delimiter='\n')
    sate = ephem.readtle(data[0], data[1], data[2])  # 3-line data for the i-th satellite "sate".
    sate.compute(mwa)
    return mwa, sate


def track_satellite(mwa, sate, time, namefmt, pixoffset=0, timeoffset=0):
    """
    Make a waterfall plot, returning data in an array of  (freq,time)
    :param mwa: ephem.Observer
    :param sate: ephem.TLE for the sattlite
    :param time: datetime
    :param namefmt: example "flagging/1102604896-sm-t{0:04d}-all-image.fits
    :param pixoffset: int, offset for pixels
    :param timeoffset: int, offset for time (seconds)
    :return: data
    """
    # Get the reference HDU
    ref = fits.getheader(namefmt.format(0))
    # determine the extent of the image
    xmax, ymax = ref['NAXIS1'], ref['NAXIS2']

    for t in range(ntimes):
        # filename for this time interval
        fname = namefmt.format(t)
        # load wcs from file
        wcs = WCS(fits.getheader(fname), naxis=2)
        # determine the time that this file represents
        tnow = time + timedelta(seconds=t+timeoffset)

        # calculate the satellite location in image coords
        mwa.date = tnow
        sate.compute(mwa)
        xy = wcs.all_world2pix([[np.degrees(sate.ra.real), np.degrees(sate.dec.real)]], 1)[0]

        # round/offset if required
        x = int(np.floor(xy[0]))+pixoffset
        y = int(np.floor(xy[1]))+pixoffset
        print "Time,x,y:",t, x, y

    return



if __name__ == "__main__":
    # dt is calculated from timeconvert.py --gps=
    deets = {'alouette': {'time': 1102604896, 
                          'fmin': 72335000, 
                          'namefmt': '1102604896-sm-t{0:04d}-freq-cube.fits',
                          'dt':datetime(2014, 12, 14, 15, 8, 00)
                         },
             'duchifat': {'time': 1102603216,
                          'fmin': 72335000,
                          'namefmt': '1102603216-sm-t{0:04d}-freq-cube.fits',
                          'dt':datetime(2014, 12, 14, 14, 40, 00)
                          }
             }

    for k in deets:
        v = deets[k]
        print k
        dt = v['dt'] #get_timestamp(v['time'])
        mwa, satellite = get_location_satellite(dt, satellite=k)

        fmt = 'flagging/' + v['namefmt']
        track_satellite(mwa, satellite, dt, namefmt=fmt, pixoffset=0, timeoffset=0)
