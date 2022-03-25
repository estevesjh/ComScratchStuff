import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm

from astropy.table import Table, join

from gaia_match import query_wcs_auxtel, query_gaia_data, ploting_field,\
                       get_lims, sky_match_tables, save_table

## Butler
repo = '/repo/main/butler.yaml'
instrument = 'LATISS'
extra_collection = 'u/mfl/testProcessCcd'
# collection = 'u/mfl/testProcessCcd_srcMatchFull_181e6356'

import lsst.rapid.analysis.butlerUtils as bu
butler2   = bu.makeDefaultLatissButler('NCSA', extraCollections=extra_collection)
registry2 =butler2.registry

dataset_refs = list(registry2.queryDatasets('src', collections=extra_collection))
dataset_refs = sorted(dataset_refs, key=lambda x : x.dataId['visit'])
expIds = [int(ref.dataId['visit']) for ref in dataset_refs]
nfields = len(expIds)

print(f'Querying {nfields} fields')
print(5*'-----'+'\n')
for expId in expIds[13:]:
    print('\n'+5*'-----')
    print(f'exposure: {expId}')
    exp = butler2.get('quickLookExp', detector=0, exposure=expId)
    scr = butler2.get('src', visit=expId, detector=0,collections=extra_collection).asAstropy()
    
    mask = scr['base_PsfFlux_instFlux']/scr['base_PsfFlux_instFluxErr'] > 50
    scr = scr[mask]

    mData = exp.getMetadata()

    print('Finding Gaia Sources')
    print('Field %i \n'%expId)

    print('1 - WCS Solutions')
    wheader, wcs_auxtel = query_wcs_auxtel(scr, center_ra = mData['RA'], center_dec = mData['DEC'])
    
    if bool(wheader):
        print('2 - Gaia Finding')
        tab = query_gaia_data(wcs_auxtel, border = 10, mag_limit=18, row_limit=-1)

        print('3 - Ploting results')
        #ploting_field(tab, scr, exp, expId, path='./figures/')
        x0, y0 = wcs_header['CRPIX1'], wcs_header['CRPIX2']
        ploting_field(tab, scr, exp, expId, x0=x0, y0=y0)

        print('4 - Sky Match Sources And Save Results')
        new = sky_match_tables(tab, scr, wcs_auxtel, radius=1.2)
        save_table(f'data/gaia_matched_{expId}.fits', new, wheader)