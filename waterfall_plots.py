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

    os.environ['TZ'] = 'right/UTC'  # TAI scale with 1970-01-01 00:00:10 (TAI) epoch
    time.tzset()  # Unix
    gps_timestamp = gps_time  # 1102604896
    gps_epoch_as_gps = datetime(1980, 1, 6)
    # by definition
    gps_time_as_gps = gps_epoch_as_gps + timedelta(seconds=gps_timestamp)
    gps_time_as_tai = gps_time_as_gps + timedelta(seconds=19)  # constant offset
    tai_epoch_as_tai = datetime(1970, 1, 1, 0, 0, 10)
    # by definition
    tai_timestamp = gps_time_as_tai - tai_epoch_as_tai
    tai_sec = tai_timestamp.seconds + tai_timestamp.days * 3600 * 24
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


def track_satellite(mwa, sate, namefmt, pixoffset=0, timeoffset=0):
    """
    Make a waterfall plot, returning data in an array of  (freq,time)
    :param mwa: ephem.Observer
    :param sate: ephem.TLE for the sattlite
    :param namefmt: example "flagging/1102604896-sm-t{0:04d}-all-image.fits
    :param pixoffset: int, offset for pixels
    :param timeoffset: int, offset for time (seconds)
    :return: data
    """
    # Get the reference HDU
    ref = fits.getheader(namefmt.format(0))
    # determine the extent of the image
    xmax, ymax = ref['NAXIS1'], ref['NAXIS2']

    # create empty array to hold our data
    data = np.empty((nfreqs, ntimes), dtype=np.float32) * np.nan
    print "extracting (pixoffset, timeoffset) = ", (pixoffset, timeoffset)
    for t in range(ntimes):
        # filename for this time interval
        fname = namefmt.format(t)
        # load wcs from file
        hdr = fits.getheader(fname)
        wcs = WCS(hdr, naxis=2)
        # determine the time that this file represents
        time = datetime.strptime(hdr['DATE-OBS'][:-2], '%Y-%m-%dT%H:%M:%S')
        # include the fractional seconds
        frac = float(hdr['DATE-OBS'][-2:])
        tnow = time + timedelta(seconds=timeoffset + frac)

        # calculate the satellite location in image coords
        mwa.date = tnow
        sate.compute(mwa)
        xy = wcs.all_world2pix([[np.degrees(sate.ra.real), np.degrees(sate.dec.real)]], 1)[0]

        # round/offset if required
        x = int(np.floor(xy[0])) + pixoffset
        y = int(np.floor(xy[1])) + pixoffset
        # extract the data iff the satellite is in the image
        if (0 <= x < xmax) and (0 <= y < ymax):
            d = fits.getdata(fname)[0, :, y, x]  # remember that image coors x,y are x,y in np arrays
            data[:, t] = d
            print "time:", t, "tdelta:", timeoffset+frac, "imloc:", x, y, "average: ", np.average(d)

    return data


def save_data(data, filename, fmin, **kwargs):
    """
    save data to file with f0 = fmin
    :param data: np.array of shape (time,freq)
    :param filename: output filename
    :param fmin: frequency of the first channel
    :return: None
    """
    print "Saving", filename
    head_dict = {
        'CTYPE1': 'time',
        'CRVAL1': kwargs['time'],
        'CRPIX1': 1,
        'CDELT1': 1,
        'CUNIT1': 'sec',
        'CTYPE2': 'freq',
        'CRVAL2': fmin,
        'CRPIX2': 1,
        'CDELT2': 20e3,
        'CUNIT2': 'Hz'}

    new_head = fits.Header(cards=head_dict)
    new_fits = fits.PrimaryHDU(data=data, header=new_head)
    # the recommended shortcut doesn't work
    # so we must make an HDUList
    new_fits = fits.HDUList(new_fits)
    new_fits.writeto(filename, clobber=True)
    return


if __name__ == "__main__":

    # dt is calculated from timeconvert.py --gps=
    deets = {'alouette': {'time': 1102604896,
                          'fmin': 72335000,
                          'namefmt': '1102604896-sm-t{0:04d}-freq-cube.fits',
                          },
             'duchifat': {'time': 1102603216,
                          'fmin': 72335000,
                          'namefmt': '1102603216-sm-t{0:04d}-freq-cube.fits',
                          }
             }

    for k in deets:
        if k == 'alouette':
            continue  # just do duchifat
        v = deets[k]
        print k
        # This isn't used but is required because i'm too lazy to write around it.
        dt = datetime(2014, 12, 14, 14, 40, 0)
        mwa, satellite = get_location_satellite(dt, satellite=k)

        for flag in ['flagging/', 'noflagging/']:
            # append the right directory
            fmt = flag + v['namefmt']
            for pixoffset in [0, 20]:
                name = '{0}_{1}{2:+02d}px.fits'.format(k, flag[:-1], pixoffset)
                if os.path.exists(name):
                    print "skipping {0} (exists)".format(name)
                    continue
                else:
                    print name, '...'
                data = track_satellite(mwa, satellite, namefmt=fmt, pixoffset=pixoffset, timeoffset=2)
                save_data(data, name, **v)
                print '.. done'

            for toff in [-4, 4]:
                name = '{0}_{1}{2:+02d}s.fits'.format(k, flag[:-1], toff)
                if os.path.exists(name):
                    print "skipping {0} (exists)".format(name)
                    continue
                else:
                    print name, '...'
                data = track_satellite(mwa, satellite, namefmt=fmt, pixoffset=0, timeoffset=toff+2)
                save_data(data, name, **v)
                print '.. done'
