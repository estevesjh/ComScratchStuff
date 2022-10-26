# Query the WCS solution from the bulter calibrate task
# Given a collection and a exposure id it will query the metadata information and the wcs
# author: Johnny Esteves
# created on March 23 2022

# after talking with Merlin I updated the query_main_pointing_info function
# the main changes are: 
# 1 - RA, DEC are from the boresight
# 2 - dRA, dDEC and PNT_OFFSET are computed by from lsst.rapid.analysis.utils import getExpPositionOffset
# 3 - the metadata columns now have a sufix `_MD` 
# 4 - some additional information comes from the exposure info, airmass, rotation angle, ...


import numpy as np
import pandas as pd
from datetime import date
# from lsst.rapid.analysis.utils import getExpPositionOffset
import lsst.pipe.base as pipeBase
import lsst.geom as geom
from astropy.coordinates import SkyCoord, AltAz
import astropy.units as u
from lsst.obs.lsst.translators.latiss import AUXTEL_LOCATION


fin_columns = {'DATE', 'MJD', 'EXPTIME', 'RA', 'DEC', 'AIRMASS', 'ROT_ANGLE', 'AZ',
               'EL', 'RA_MD', 'DEC_MD', 'EXPTIME_MD', 'TEMP_SET_MD', 'CCDTEMP_MD',
               'FILTER_MD', 'RA_WCS', 'DEC_WCS', 'dRA', 'dDEC', 'dAZ', 'dEL', 'PNT_OFFSET'}

nan_dict = {col: np.nan for col in fin_columns}

def getExpPositionOffset(exp1, exp2):
    # need the exps if we want altAz because we need the observation times
    wcs1 = exp1.getWcs()
    wcs2 = exp2.getWcs()
    p1 = wcs1.getSkyOrigin()
    p2 = wcs2.getSkyOrigin()

    vi1 = exp1.getInfo().getVisitInfo()
    vi2 = exp2.getInfo().getVisitInfo()

    # AltAz via astropy
    skyLocation1 = SkyCoord(p1.getRa().asRadians(), p1.getDec().asRadians(), unit=u.rad)
    altAz1 = AltAz(obstime=vi1.date.toPython(), location=AUXTEL_LOCATION)
    obsAltAz1 = skyLocation1.transform_to(altAz1)
    alt1 = geom.Angle(obsAltAz1.alt.degree, geom.degrees)
    az1 = geom.Angle(obsAltAz1.az.degree, geom.degrees)

    skyLocation2 = SkyCoord(p2.getRa().asRadians(), p2.getDec().asRadians(), unit=u.rad)
    altAz2 = AltAz(obstime=vi2.date.toPython(), location=AUXTEL_LOCATION)
    obsAltAz2 = skyLocation2.transform_to(altAz2)
    alt2 = geom.Angle(obsAltAz2.alt.degree, geom.degrees)
    az2 = geom.Angle(obsAltAz2.az.degree, geom.degrees)

    # ra/dec via the stack
    # NB using the wcs not the exp visitInfo as that's unfitted
    # and so is always identical for a given object/pointing
    ra1 = p1[0]
    ra2 = p2[0]
    dec1 = p1[1]
    dec2 = p2[1]

    angular_offset = p1.separation(p2).asArcseconds()
    delta_pixels = angular_offset / wcs1.getPixelScale().asArcseconds()

    ret = pipeBase.Struct(deltaRa=ra1-ra2,
                          deltaDec=dec1-dec2,
                          deltaAlt=alt1-alt2,
                          deltaAz=az1-az2,
                          delta_pixel_magnitude=delta_pixels,
                          angular_offset_arcsec=angular_offset
                          )

    return ret

def getSkyOriginValues(wcsInfo):
    ra = wcsInfo.getSkyOrigin().getRa().asDegrees()
    dec = wcsInfo.getSkyOrigin().getDec().asDegrees()
    return ra, dec

def get_exposure_info(exposure):
    info = exposure.getInfo()
    vi = info.getVisitInfo()

    expTime = vi.getExposureTime()
    date = vi.getDate().toPython()
    mjd = vi.getDate().get()

    airmass = vi.getBoresightAirmass()
    rotangle = vi.getBoresightRotAngle().asDegrees()
    
    raDec = vi.boresightRaDec
    ra = raDec[0].asDegrees()
    dec = raDec[1].asDegrees()
    
    azAlt = vi.getBoresightAzAlt()
    az = azAlt[0].asDegrees()
    el = azAlt[1].asDegrees()
    
    info = {'DATE': date, 'MJD': mjd, 'EXPTIME': expTime, 'RA': ra, 'DEC': dec,
            'AIRMASS': airmass, 'ROT_ANGLE': rotangle, 'AZ':az, 'EL':el}
    return info

def query_main_pointing_info(expId, expIdend=0):
    #day_obs = int(str(expId)[:8])
    day_obs = int(str(expId)[-13:][:8]) # robust query day because of a 9 in the front
    dataId = {"instrument": instrument, "exposure.day_obs": day_obs, "visit": expId, "detector": 0}
    
    # try:
    raw = butler.get('raw', dataId)
    fitted = butler.get('calexp', dataId)
    offset = getExpPositionOffset(raw, fitted)

    # get offset
    dRa = offset.deltaRa.asArcminutes()
    dDec = offset.deltaDec.asArcminutes()
    dAz = offset.deltaAz.asArcminutes()
    dEl = offset.deltaAlt.asArcminutes()
    angular_offset = offset.angular_offset_arcsec/60. # arcminutes

    # get pointing
    wcsFitted = fitted.getWcs()
    ra, dec = getSkyOriginValues(wcsFitted)

    # get metadata
    mData = raw.getMetadata().toDict()#butler.get('raw.metadata', dataId).toDict()

    # querying some basic info about the exposure
    info = get_exposure_info(raw)

    for col in mylist:
        info[col+'_MD'] = mData[col] 

    info['RA_WCS'] = ra
    info['DEC_WCS'] = dec
    info['dRA'] = dRa
    info['dDEC'] = dDec
    info['dAZ'] = dAz
    info['dEL'] = dEl
    info['PNT_OFFSET'] = angular_offset
    print(f'Completed {expId}/{expIdend}')
    # except:
    #     print('Failed to run %i'%expId)
    #     info = nan_dict
    df = pd.DataFrame(info, index=np.array([expId]))
    df.to_csv(f'data/tmp/checking_auxtel_pointing_{TAG}_{expId}.csv')

TAG = 'Oct2022'
nCores = 10
# metada columns it would be stored
mylist = ['RA','DEC','EXPTIME','TEMP_SET','CCDTEMP','FILTER']

# initializating the butler repo
repo = '/repo/main/butler.yaml'
repo_2 = '/project/edennihy/auxtelImagingSurveys/data/'
repo_3 = '/sdf/group/rubin'+repo
repo_4 = '/sdf/group/rubin/repo/oga/butler.yaml'

instrument = 'LATISS'
# collection = 'u/mfl/testProcessCcd'
# collection = 'u/mfl/testProcessCcd_srcMatchFull_181e6356'
# collection = 'u/edennihy/tickets/CAP-868_20220321a'
# collection = 'u/edennihy/tickets/CAP-851'
# collection = 'u/edennihy/tickets/SITCOM-266_20220419'
# collection = 'u/edennihy/CAP-886_partial'
# collection = 'u/edennihy/tickets/SITCOM-306_piff' # May 2022
collection = 'u/edennihy/tickets/SITCOM-484' # Oct 2022

print('\n')
print('Querying WCS Poiting')
print(f'repo: {repo}')
print(f'collection: {collection} \n')

# import lsst.rapid.analysis.butlerUtils as bu
# butler = bu.makeDefaultLatissButler('NCSA', extraCollections=[collection])
# registry=butler.registry

import lsst.daf.butler as dafButler #Gen3 butler
butler = dafButler.Butler(repo_4, collections=[collection])
registry=butler.registry

# querying all exposure ids in this collection
dataset_refs = list(registry.queryDatasets('calexp', collections=collection))
dataset_refs = sorted(dataset_refs, key=lambda x : x.dataId['visit'])
expIds = np.array([int(ref.dataId['visit']) for ref in dataset_refs])

# # just today (26th Oct)
# df = pd.read_csv('data/checking_auxtel_pointing_Oct2022.csv',index_col=0)
# isnan = np.where(np.isnan(df['MJD'].to_numpy()))
# expIds = df.index.to_numpy()[isnan]

# for test purposes only
# expIds = expIds[:10]

print('\nStarting Query')
print(f'Number of exposures: {len(expIds)}')
from joblib import Parallel, delayed
tables = Parallel(n_jobs=nCores)(delayed(query_main_pointing_info)(expId, expIdend=expIds[-1]) for expId in expIds)

# querying the wcs poiting and the metadata info
# tables = []
# for expId in expIds:
#     print(f'exposure: {expId}')
#     tables.append(query_main_pointing_info(expId, butler, expIds[-1]))
#     print('\n')
                   
# saving output as pandas dataframe
df = pd.DataFrame(tables, index=np.array(expIds))

date = date.today().strftime("%d%m%Y")
print(f'Date: {date}')
df.to_csv(f'data/checking_auxtel_pointing_{TAG}.csv')
print(f'Saved file: data/checking_auxtel_pointing_{TAG}.csv')
