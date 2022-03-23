# Query the WCS solution from the bulter calibrate task
# Given a collection and a exposure id it will query the metadata information and the wcs
# author: Johnny Esteves
# created on March 23 2022

import numpy as np
import pandas as pd
from datetime import date

def getSkyOriginValues(wcsInfo):
    ra = wcsInfo.getSkyOrigin().getRa().asDegrees()
    dec = wcsInfo.getSkyOrigin().getDec().asDegrees()
    return ra, dec

def query_wcs_pointing(dataId):
    wcsInfo = butler.get('calexp.wcs', dataId)
    ra, dec = getSkyOriginValues(wcsInfo)
    return ra, dec

def query_main_pointing_info(expId):
    day_obs = int(str(expId)[:8])
    dataId = {"instrument": instrument, "exposure.day_obs": day_obs, "visit": expId, "detector": 0}

    ra, dec = query_wcs_pointing(dataId)
    
    mData = butler.get('raw.metadata', dataId).toDict()
    myinfo = {k:mData[k] for k in mylist}
    myinfo['RA_WCS'] = ra
    myinfo['DEC_WCS'] = dec
    
    return myinfo

# metada columns it would be stored
mylist = ['RA','DEC','MJD','EXPTIME','TEMP_SET','CCDTEMP','FILTER',
          'ELSTART','ELEND','AZSTART','AZEND']

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
df.to_csv(f'data/checking_auxtel_pointing_{date}.csv')
print(f'Saved file: data/checking_auxtel_pointing_{date}.csv')