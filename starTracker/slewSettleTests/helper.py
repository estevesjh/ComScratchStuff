import numpy as np
import pandas as pd

# function to read in the metadata that has been downloaded
def read_rubintv(date):
    fname = 'startracker_%s.json'%date
    
    df = pd.read_json(fname).T
    df = df.dropna()
    times = df[['UTC','UTC wide']]
    
    df = df.drop(columns=['UTC','UTC wide'])
    df = df.astype(float)
    
    # set time vectors
    timenew = (date+'T'+ times['UTC'].to_numpy()).astype(np.datetime64)
    timenew2= (date+'T'+ times['UTC wide'].to_numpy()).astype(np.datetime64)
    
    df['UTC'] = pd.Series(timenew, index=df.index)
    df['UTC wide'] = pd.Series(timenew2, index=df.index)
    df['seq_num'] = df.index
    return df

def get_groups(df):
    """ Find same target images
    """
    ra = df['Calculated Ra wide'].to_numpy()
    dec = df['Calculated Dec wide'].to_numpy()

    groups = np.zeros(ra.size, dtype=int)
    diffRa = np.diff(ra)
    diffDec = np.diff(dec)
    dPnt = np.hypot(diffDec, diffRa)
    
    counter = 0
    for i in range(diffRa.size):
        if  (dPnt[i]>60/3600): counter += 1    
        groups[i+1] = counter

    df['groups'] = groups
    print('Number of Groups: %i'%np.unique(groups).size)
    return df

def get_snakes(data):
    """ Find Snakes
    
    The snakes are circles with 3.5deg radii
    Select the ones with Angular difference higher than 7deg. 
    The Angular difference is Euclidean, for this reason ang_offset needs to be larger than 3.5
    """
    ang_offset = 7. # carefully choosen based on the datasets in hand
    
    pnt = np.hypot(data['Calculated Ra wide'].diff(), data['Calculated Dec wide'].diff()).to_numpy()
    sids = np.append(np.array([0]),np.where(pnt>ang_offset)[0])
    counts = np.diff(sids)
    snakes = np.zeros_like(data['groups'].to_numpy())
    for i in range(len(sids)-1):
        snakes[sids[i]:sids[i]+counts[i]] = i
    data['snakes'] = snakes
    return data

def get_residual(ycol, df, keys):
    yvec = df[ycol].to_numpy()
    res = np.zeros_like(yvec)
    for ix in keys:
        res[ix] = (yvec[ix]-np.mean(yvec[ix]))*3600
    return res

def get_baseline(ycol, df, keys):
    yvec = df[ycol].to_numpy()
    base = np.zeros_like(yvec)
    for ix in keys:
        base[ix] = np.mean(yvec[ix])
    return base

def get_residual_2(ycol, df, keys):
    yvec = df[ycol].to_numpy()
    res = np.zeros_like(yvec)
    for ix in keys:
        res[ix] = (yvec[ix]-yvec[ix][0])*3600
    return res

def get_baseline_2(ycol, df, keys):
    yvec = df[ycol].to_numpy()
    base = np.zeros_like(yvec)
    for ix in keys:
        base[ix] = yvec[ix][0]
    return base

def filter_sequences(df, sequences):
    indices = np.empty((0,),dtype=int)
    for i0, ie in sequences:
        _indices = np.arange(np.where(df['seq_num']==i0)[0][0], np.where(df['seq_num']==ie)[0][0], 1)
        indices = np.append(indices, _indices)
    
    return df.iloc[indices].copy()

def filter_groups(data):
    gids, _, counts = np.unique(data['groups'].to_numpy(), return_index=True, return_counts=True)
    is_group = counts<=5
    ngroups = np.count_nonzero(is_group)
    # filter
    mask = np.in1d(data['groups'].to_numpy(), gids[is_group])
    data = data.iloc[mask].copy()
    return data, ngroups
