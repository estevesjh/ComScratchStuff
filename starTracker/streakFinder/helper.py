import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.stats import sigmaclip
from mpl_toolkits.axes_grid1 import make_axes_locatable

# https://stackoverflow.com/questions/26574945/how-to-find-the-center-of-circle-using-the-least-square-fit-in-python

import matplotlib
matplotlib.rcParams["image.interpolation"] = 'nearest'

def display(imArr, nStd = 5, gSig = 7, ax=None, fig=None):
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=(12,12))
    imArrClip, low, high = sigmaclip(imArr)
    mean = imArrClip.mean()
    std = imArrClip.std()
    im = ax.imshow(imArr, vmin=mean-nStd*std, vmax=mean+nStd*std, cmap='gray', origin='lower')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im, cax=cax, orientation='vertical')

def read_image(filename):
    with fits.open(filename) as hdu:
        imArr = hdu[0].data
    return imArr


def apply_filter(A, smoothing, power=2.0):
    """Apply a hi/lo pass filter to a 2D image.
    
    The value of smoothing specifies the cutoff wavelength in pixels,
    with a value >0 (<0) applying a hi-pass (lo-pass) filter. The
    lo- and hi-pass filters sum to one by construction.  The power
    parameter determines the sharpness of the filter, with higher
    values giving a sharper transition.
    """
    if smoothing == 0:
        return A
    ny, nx = A.shape
    # Round down dimensions to even values for rfft.
    # Any trimmed row or column will be unfiltered in the output.
    nx = 2 * (nx // 2)
    ny = 2 * (ny // 2)
    T = np.fft.rfft2(A[:ny, :nx])
    # Last axis (kx) uses rfft encoding.
    kx = np.fft.rfftfreq(nx)
    ky = np.fft.fftfreq(ny)
    kpow = (kx ** 2 + ky[:, np.newaxis] ** 2) ** (power / 2.)
    k0pow = (1. / smoothing) ** power
    if smoothing > 0:
        F = kpow / (k0pow + kpow) # high pass
    else:
        F = k0pow / (k0pow + kpow) # low pass
    S = A.copy()
    S[:ny, :nx] = np.fft.irfft2(T * F)
    return S