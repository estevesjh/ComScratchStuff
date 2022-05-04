import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import gaussian_kde
from sklearn.neighbors import KernelDensity

def kde_sklearn(x, x_grid, bandwidth=0.2, **kwargs):
    """Kernel Density Estimation with Scikit-learn"""
    kde_skl = KernelDensity(bandwidth=bandwidth, **kwargs)
    kde_skl.fit(x[:, np.newaxis])
    # score_samples() returns the log-likelihood of the samples
    log_pdf = kde_skl.score_samples(x_grid[:, np.newaxis])
    return np.exp(log_pdf)

def compute_fraction_kde_sklearn(xvec, x, mask, bw=None, rtol=1e-6, kernel='gaussian', eps=1e-6):
    N1, N2 = len(x), len(x[mask])
    numerator = N2*kde_sklearn(x[mask], xvec, bandwidth=bw, rtol=rtol, kernel=kernel)
    denumerator = N1*kde_sklearn(x, xvec, bandwidth=bw, rtol=rtol, kernel=kernel)+eps
    frac = numerator/denumerator
    return np.where(frac>1., np.nan, frac)

def compute_kde(x,bw=None):
    Norm = len(x)
    pdf = gaussian_kde(x, bw_method=bw)
    return pdf, Norm

def compute_fraction_kde(xvec, x, mask, bw=None, eps=1e-3):
    pdf1, N1 = compute_kde(x, bw=bw)
    if bw is None: bw = pdf1.scotts_factor()
    pdf2, N2 = compute_kde(x[mask], bw=bw)
    denumerator = N1*pdf1(xvec)
    frac = N2*pdf2(xvec)/denumerator
    return np.where(frac>1., np.nan, frac)

def compute_fraction_err(mvec, mag, mask, bw=0.01, nBootStrap=100, error=True):
    nsize = len(mvec)
    frac = np.full((nsize, nBootStrap), np.nan)
    if error:
        for i in range(nBootStrap):
            idx = sample_vec(mag) # similar to: df.sample(frac=1, replace=True)
            #frac[:,i] = compute_fraction_kde(mvec, mag[idx], mask[idx], bw=bw)
            frac[:,i] = compute_fraction_kde_sklearn(mvec, mag[idx], mask[idx], bw=bw)
    else:
        fr = compute_fraction_kde_sklearn(mvec, mag, mask, bw=bw)
        for i in range(nBootStrap):
            frac[:,i] = fr
    return frac

def sample_vec(x):
    idx = np.random.randint(0,x.size,size=x.size,dtype=int)
    return idx

def plot_curve(x, y, percentiles=[16,84],ax=None,color=None,**args):
    if ax is None: ax = plt.axes()
    
    ylow = np.nanpercentile(y,percentiles[0],axis=1)
    yhig = np.nanpercentile(y,percentiles[1],axis=1)
    ymean = np.nanmedian(y,axis=1)
    
    p = ax.plot(x,ymean,color=color,**args)
    ax.fill_between(x,ylow,yhig,color=p[0].get_color(),alpha=0.3)
    
    #ax.scatter(x,ymean, s=1,color=color,**args)