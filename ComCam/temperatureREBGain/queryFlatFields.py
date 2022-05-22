import sys, os, glob, time
import asyncio
import numpy as np
import astropy.io.fits as pf
import matplotlib.pyplot as plt
import lsst.daf.butler as dafButler

import pandas as pd
from lsst.summit.utils.bestEffort import BestEffortIsr
from joblib import Parallel, delayed

nCores = 12
outname = 'data/flat_field_pairs_auxTel_2022_{}.csv'

print('Starting Code')
def get_flux(day, seq):
    dataId = {'day_obs': day, 'seq_num': seq, 'detector':0}
    exp = bestEffort.getExposure(dataId)
    return np.nanmedian(exp.image.array.flatten())

bestEffort = BestEffortIsr()
butler = dafButler.Butler("/repo/main", collections=["LATISS/raw/all","LATISS/calib"])
registry = butler.registry

# find all days with an exposure
refs = sorted(registry.queryDatasets('raw', collections=["LATISS/raw/all","LATISS/calib"], instrument='LATISS'))
exposure_all = [int(refs[i].dataId['exposure']) for i in range(len(refs))]
days_all = [int(str(exposure)[:8]) for exposure in exposure_all]
days_all = np.unique(days_all)

# taking exposures since 2021
days = days_all[(days_all>20210000)&(days_all<20230000)]
days = np.flip(days,0)

print('Searching for all flats')
# find all the flats
flat_ids = []
info_list = []
for dayObs in days:
    exposureList = []
    for record in butler.registry.queryDimensionRecords("exposure", where="exposure.day_obs=%d"%dayObs):
        exposureList.append([record.id, record])
    exposureList.sort(key=lambda x: x[0])
    for [id,record] in exposureList:
        info_dict = dict()
        if record.observation_type=='flat':
            info_dict['day'] = int(record.day_obs)
            info_dict['seq_num'] = int(record.seq_num)
            info_dict['exposure_id'] = int(record.id)
            info_dict['exposure_time'] = float(record.exposure_time)
            info_dict['time'] = record.timespan.begin.isot
            flat_ids.append(int(record.id))
            info_list.append(info_dict)

df = pd.DataFrame(info_list, index=np.array(flat_ids))

df_all = df.to_numpy().T
exposures = df_all[2]
days = df_all[0]
seq_num = df_all[1]
exp_time = df_all[3]

# flat pairs
# are consecutives exposures on the same day
# with exposure time lower than 20 sec
exp_time_th = exp_time[1:]<20.
consec_exposures = ((seq_num[1:]-seq_num[:-1])==1)&(days[1:]==days[:-1])
pairs = (exp_time[1:] == exp_time[:-1])&(consec_exposures)&exp_time_th
pairs_idx = np.where(pairs)[0]

# for tests purposes
# pairs_idx = pairs_idx[:8]
good_indices = np.unique(np.hstack([pairs_idx,pairs_idx+1]))
good_indices = good_indices[np.argsort(-1*exposures[good_indices])]

print('Number of good flats %i'%len(good_indices))
df.iloc[good_indices].to_csv(outname.format('raw'))
print('First file saved: %s'%(outname.format('raw')))

# get the corrected flux
t0 = time.time()
fluxes = Parallel(n_jobs=nCores)(delayed(get_flux)(days[i], seq_num[i]) for i in good_indices)
flux_time = time.time()-t0
print('Time to query fluxes: %.2f s'%flux_time)

flux_array = np.full(len(df), np.nan)
flux_array[good_indices] = np.array(fluxes)
df['Flux'] = flux_array
df.iloc[good_indices].to_csv(outname.format('flux'))
print('Second file saved: %s'%(outname.format('flux')))

# get the temperature
# from lsst_efd_client import EfdClient, resample
# efd_client = EfdClient('ldf_stable_efd')

# temp_data = np.full(len(df), np.nan, 
#                     dtype=[('t1', float), 
#                           ('t1_err', float),
#                           ('t2', float), 
#                           ('t2_err', float)])

# # get the temperature
# for ii in pairs_idx:
#     exposure = exposures[ii]
#     time1 = Time(times[ii], format='isot', scale='tai')
#     time2 = Time(times[ii+1], format='isot', scale='tai')
    
#     if exposure < 20211013:
#         # EFD was switched to UTC on 20211013.  This compensates for that.
#         tai_offset = 37.0
#     else:
#         tai_offset = 0.0
#     t1 = time1 - TimeDelta(-10., format='sec', scale='tai')
#     t2 = time2 + TimeDelta(+10., format='sec', scale='tai')
    
#     res1 = asyncio.run(efd_client.select_time_series("lsst.sal.ATCamera.focal_plane_Reb", 
#                                                ["aspicl_Temp00","aspicu_Temp00"], 
#                                                t1.utc - TimeDelta(tai_offset, format='sec'), 
#                                                t2.utc - TimeDelta(tai_offset, format='sec'))
#                       )
#     if len(res1)>0:
#         t1 = np.mean(res1['aspicl_Temp00'])
#         t1_err = np.std(res1['aspicl_Temp00'])
#         t2 = np.mean(res1['aspicu_Temp00'])
#         t2_err = np.std(res1['aspicu_Temp00'])

#         temp_data[ii] = (t1, t1_err, t2, t2_err)
#         temp_data[ii+1] = (t1, t1_err, t2, t2_err)

# # np.save('data/temp_bla.npy', temp_data)
# df['Temp1'] = temp_data['t1']
# df['TempErr1'] = temp_data['t1_err']
# df['Temp2'] = temp_data['t2']
# df['TempErr2'] = temp_data['t2_err']
# df.iloc[good_indices].to_csv(outname.format('flux_temp'))
# print('First file saved: %s'%(outname.format('flux_temp')))
