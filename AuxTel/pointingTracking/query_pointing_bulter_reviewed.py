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
from lsst.rapid.analysis.utils import getExpPositionOffset

mylist = ['RA','DEC','EXPTIME','TEMP_SET','CCDTEMP','FILTER',
          'ELSTART','ELEND','AZSTART','AZEND','ELSTART']

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

def query_main_pointing_info(expId):
    day_obs = int(str(expId)[:8])
    dataId = {"instrument": instrument, "exposure.day_obs": day_obs, "visit": expId, "detector": 0}
    
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
    return info

# metada columns it would be stored
mylist = ['RA','DEC','EXPTIME','TEMP_SET','CCDTEMP','FILTER',
          'ELSTART','ELEND','AZSTART','AZEND','ELSTART']

# initializating the butler repo
repo = '/repo/main/butler.yaml'
instrument = 'LATISS'
# collection = 'u/mfl/testProcessCcd'
collection = 'u/mfl/testProcessCcd_srcMatchFull_181e6356'

print('\n')
print('Querying WCS Poiting')
print(f'repo: {repo}')
print(f'collection: {collection} \n')

import lsst.rapid.analysis.butlerUtils as bu
butler = bu.makeDefaultLatissButler('NCSA', extraCollections=[collection])
registry=butler.registry

# querying all exposure ids in this collection
dataset_refs = list(registry.queryDatasets('calexp', collections=collection))
dataset_refs = sorted(dataset_refs, key=lambda x : x.dataId['visit'])
expIds = [int(ref.dataId['visit']) for ref in dataset_refs]

# for test purposes only
# expIds = expIds[:10]

print('\nStarting Query')
print(f'Number of exposures: {len(expIds)}')

# querying the wcs poiting and the metadata info
tables = []
for expId in expIds:
    print(f'exposure: {expId}')
    tables.append(query_main_pointing_info(expId))
    print('\n')

# saving output as pandas dataframe
df = pd.DataFrame(tables, index=np.array(expIds))
date = date.today().strftime("%d%m%Y")
df.to_csv(f'data/rev_checking_auxtel_pointing_{date}.csv')
print(f'Saved file: data/rev_checking_auxtel_pointing_{date}.csv')