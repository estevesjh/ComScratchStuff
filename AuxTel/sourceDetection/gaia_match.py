from astroquery.gaia import Gaia

## astropy
from astropy.table import table, join
from astropy.io import fits
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
import smatch

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm
from matplotlib.patches import Circle

# ## Astromety.net
# from astroquery.astrometry_net import AstrometryNet
# ast = AstrometryNet()
# ast.api_key = 'xxawwhvleirxcswx'

import warnings
from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

image_width = 4072
image_height = 4000
scale_units = 'arcsecperpix'
scale_type='ev' # ev means submit estimate and % error
scale_est = 0.095
scale_err = 2.0

mycolumns = ['source_id','ra','dec','phot_g_mean_mag','phot_bp_mean_mag','phot_rp_mean_mag','radius_val']
mycolumns_flat = ', '.join(map(str, mycolumns))

def query_wcs_auxtel(sources, center_ra=0, center_dec=0, radius = 0.5, timeout=240):
    """Queries on astromety.net the wcs solution for the AuxTel Telescope

    input: src table - `src` from the DM stack
    output: wcs_header, wcs
    """
    ## Astromety.net
    from astroquery.astrometry_net import AstrometryNet
    ast = AstrometryNet()
    ast.api_key = 'xxawwhvleirxcswx'

    sources.keep_columns(['base_SdssCentroid_x', 'base_SdssCentroid_y', 'base_CircularApertureFlux_3_0_instFlux'])
    sources.sort('base_CircularApertureFlux_3_0_instFlux', reverse=True)
    # Keep just the 17 bright sources
    #sources.remove_rows(slice(17, 53, 1))
    try:
        wcs_header = ast.solve_from_source_list(sources['base_SdssCentroid_x'], sources['base_SdssCentroid_y'],
                                                image_width, image_height, scale_units=scale_units,
                                                scale_type=scale_type, scale_est=scale_est, scale_err=scale_err,
                                                center_ra=center_ra, center_dec=center_dec, radius=radius,
                                                solve_timeout=timeout)
    except:
        print('Error: wcs query was not complted')
        wcs_header = dict()
        
    # define the wcs object
    w = WCS(wcs_header)
    return wcs_header, w

def make_rectangle(x1, x2, y1, y2):
    """Return the corners of a rectangle."""
    xs = [x1, x1, x2, x2, x1]
    ys = [y1, y2, y2, y1, y1]
    return np.array(xs), np.array(ys)

def make_point_list(xs,ys):
    point_list = []
    for ri,di in zip(xs,ys):
        point_list.append(str(ri))
        point_list.append(str(di))
    return ', '.join(point_list)


def query_gaia_data(wcs_auxtel, border = 10, mag_limit=18, row_limit=-1, is_butler=False):
    # trasnform the corners from physical coord to wcs 
    xRect, yRect = make_rectangle(0-border, image_width+border, 0-border, image_height+border)
    
    if is_butler:
        ra, dec = wcs_auxtel.pixelToSkyArray(xRect.astype(float), yRect.astype(float), degrees=True)
    else:
        corners_wcs = wcs_auxtel.pixel_to_world(ra_rect,dec_rect)
        ra, dec = corners_wcs.ra.deg, corners_wcs.dec.deg
    
    # make a point list for the polygon function, Note: order matters here! 
    point_list = make_point_list(ra, dec)
    query = f"""SELECT 
    {mycolumns_flat}
    FROM gaiadr2.gaia_source
    WHERE phot_g_mean_mag < {mag_limit}
    AND 1 = CONTAINS(POINT(ra, dec), 
                    POLYGON({point_list}))
    """
    #print('\n')

    # print('starting query:')
    # print(query)
    # print('\n')

    Gaia.ROW_LIMIT = row_limit
    job = Gaia.launch_job(query)
    tab = job.get_results()
    
    if is_butler:
        pixel_list = wcs_auxtel.skyToPixelArray(np.array(tab['ra']), np.array(tab['dec']), degrees=True)
    else:
        coords = SkyCoord(ra=np.array(tab['ra'])*u.degree, dec=np.array(tab['dec'])*u.degree, frame="icrs")
        pixel_list = wcs_auxtel.world_to_pixel(coords)

    tab['ref_base_SdssCentroid_x'] = pixel_list[0]
    tab['ref_base_SdssCentroid_y'] = pixel_list[1]
    
    tab.rename_column('ra','ref_ra')
    tab.rename_column('dec','ref_dec')
    print('%i sources selected on the field'%len(tab))
    return tab

def joining_tables(ref_table, table, id0, id1):
    ## joinining tables
    sources = table.copy()
    sources.keep_columns(['ra','dec','base_SdssCentroid_x', 'base_SdssCentroid_y', 
                          'base_CircularApertureFlux_3_0_instFlux', 'base_CircularApertureFlux_3_0_instFluxErr',
                          'gaia'])
    
    sources.sort('base_CircularApertureFlux_3_0_instFlux', reverse=True)
    
    ref_table['id_match'] = -1
    sources['id_match'] = -2
    
    if len(id1)>0:
        ids = np.arange(len(id1),dtype=int)
        ref_table['id_match'][id0] = id1
        sources['id_match'][id1] = id1

    new = join(sources, ref_table, keys='id_match',join_type='outer')
    return new

def sky_match_tables(ref_table, table, wcs_auxtel, radius=1.2, is_butler=False):
    ra1 = np.array(ref_table['ref_ra'])
    dec1 = np.array(ref_table['ref_dec'])

    ## converting pixel coordinates to sky coord
    x = np.array(table['base_SdssCentroid_x'])
    y = np.array(table['base_SdssCentroid_y'])
    
    if is_butler:
        sky_list = wcs_auxtel.pixelToSkyArray(x.astype(float), y.astype(float), degrees=True)
    else:
        sky_list = wcs_auxtel.pixel_to_world_values(x,y)
    ra2 = sky_list[0]
    dec2 = sky_list[1]
    
    table['ra'] = sky_list[0]
    table['dec']= sky_list[1]
    
    ## sky matching
    nside=4096 # healpix nside
    maxmatch=1 # return closest match

    # ra,dec,radius in degrees
    matches = smatch.match(ra1, dec1, radius/3600, ra2, dec2, nside=nside, maxmatch=maxmatch)
    
    id0 = matches['i1']
    id1 = matches['i2']
    ref_table['dist'] = -1
    table['gaia'] = False
    ref_table['auxtel'] = False
    
    if len(id0)>0:
        dist = separation(ra1[id0],dec1[id0],ra2[id1],dec2[id1]) ## only works for some arcsecs
        ref_table['dist'][id0] = dist
        table['gaia'][matches['i2']] = True
        ref_table['auxtel'][matches['i1']] = True
    
    new = joining_tables(ref_table, table, id0, id1)
    
    return new

def save_table(fname, table, header=None):
    table.write(fname, format='fits', overwrite=True)
    
    if header is not None:
        # saving header
        hdul = fits.open(fname)
        hdul[0].header = header
        hdul.writeto(fname,overwrite=True)
    print(f'table saved: {fname}')
    
    
def get_lims(x):
    q1,q2,q3 = np.nanpercentile(x,[25,50,75])
    iqr = (q3-q1)*0.5
    return (q1-1.5*iqr),(q3+1.5*iqr)

deg = np.pi/180.
def separation(ra1,dec1,ra2,dec2):
    return np.sqrt( np.cos(dec1*deg)*(ra1-ra2)**2 + (dec1-dec2)**2 )*3600.

# def check_wcs(fname,threshold):
#     tb = Table(fits.getdata(fname))
#     hdu = fits.open(fname)
#     wh = hdu[0].header
#     w = WCS(wh)
    
#     try:
#         x = np.array(tb['base_SdssCentroid_x'])
#         y = np.array(tb['base_SdssCentroid_y'])
#         ra = tb['ra']
#         dec = tb['dec']

#         sky = w.pixel_to_world_values(x,y)
#         dist = separation(sky[0],sky[1],ra,dec)
#         frac = np.count_nonzero(dist<0.8)/np.count_nonzero(dist<10.)
#     except:
#         print('Error: this table was not matched')
#         frac = 0.
#     return frac > threshold

def get_image_limits(x, ns = 1.5):
    p1,pm,p3 = np.nanpercentile(x,[16,50,84])
    low_limit = (p1-ns*(p3-p1))
    vhig = (p3+ns*(p3-p1))-low_limit
    vlow = p1-low_limit
    return low_limit, vlow, vhig

def ploting_field(tab, scr, exposure, expId,path='.', x0=2000.0, y0=2000.0):
    mData = exposure.getMetadata()
    image_array = exposure.image.array
    low_limit, vmin, vmax = get_image_limits(image_array.flatten())
    image_array -= low_limit
    #vmin, vmax = get_lims(image_array.flatten())
    
    mask = scr['base_CircularApertureFlux_3_0_instFlux']/scr['base_CircularApertureFlux_3_0_instFluxErr'] > 50
    
    #x0, y0 = wcs_header['CRPIX1'], wcs_header['CRPIX2']

    if vmin<0: vmin=10.5
    image_array = np.clip(image_array, 1., 100*vmax) # This image has some negative values, and this removes them

    fig = plt.figure(figsize=(12+1,12))
    # fig.add_subplot(111, projection=w)
    ax = fig.add_subplot(111)

    img = plt.imshow(image_array, norm=LogNorm(vmin=vmin, vmax=3*vmax),  interpolation='Nearest', cmap='gray')

    ax.scatter(tab['ref_base_SdssCentroid_x'],tab['ref_base_SdssCentroid_y']\
                ,facecolors='none', edgecolors='g', s=200, lw=2, label='Gaia Sources [< 28 mag]')

    ax.scatter(scr['base_SdssCentroid_x'][mask],scr['base_SdssCentroid_y'][mask]\
                ,color='b', marker='x',label='DM Sources')

    ax.scatter(x0, y0,color='r',s=300,marker='x',label='AuxTel WCS Position')
    ax.legend(fontsize=16)
    ax.set_ylim(0,image_height)
    ax.set_xlim(0,image_width)
    ax.set_aspect('equal')
    ax.set_title(f'Field: {expId}',fontsize=16)
    plt.show()
    fig.tight_layout()
    fig.savefig(f'{path}/gaia_{expId}.png', facecolor='w',transparent=False, dpi=75)
    plt.clf()
    print(f'saved file: {path}/gaia_{expId}.png')

def query_gaia_tables():
    day_obs = int(str(expId)[:8])
    dataId = {"instrument": instrument, "exposure.day_obs": day_obs, "visit": expId, "detector": 0}

    exp = butler.get('calexp', dataId)
    scr = butler.get('src', visit=expId, detector=0, collections=extra_collection).asAstropy()

    # mask = scr['base_PsfFlux_instFlux']/scr['base_PsfFlux_instFluxErr'] > 50
    # scr = scr[mask]

    mData = butler.get('raw.metadata', dataId).toDict()

    print('Finding Gaia Sources')
    print('Field %i \n'%expId)

    print('1 - WCS Solutions')
    # wheader, wcs_auxtel = query_wcs_auxtel(scr, center_ra = mData['RA'], center_dec = mData['DEC'])
    wcsButler = butler.get('calexp.wcs', dataId)
    #x0, y0    = wcsButler.getPixelOrigin().getX(), wcsButler.getPixelOrigin().getY()

    print('2 - Gaia Finding')
    tab = query_gaia_data(wcsButler, border = 10, mag_limit=18, row_limit=-1, is_butler=True)

    print('3 - Ploting results')
    ploting_field(tab, scr, exp, expId, x0=x0, y0=y0)

    # wheader = write_metadata(mData)

    print('4 - Sky Match Sources And Save Results')
    new = sky_match_tables(tab, scr, wcsButler, radius=1.2, is_butler=True)
    new['DATE'] = str(mData['DATE'])
    new['FILTER'] = mData['FILTER']
    new['EXPTIME'] = mData['EXPTIME']
    save_table(f'data/gaia_matched_{expId}.fits', new, mData)

# if __name__ == "__main__":