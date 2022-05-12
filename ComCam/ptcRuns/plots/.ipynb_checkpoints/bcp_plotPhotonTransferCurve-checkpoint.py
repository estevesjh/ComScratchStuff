import lsst.cp.pipe.plotPtc
assert type(config)==lsst.cp.pipe.plotPtc.PlotPhotonTransferCurveTaskConfig, 'config is of type %s.%s instead of lsst.cp.pipe.plotPtc.PlotPhotonTransferCurveTaskConfig' % (type(config).__module__, type(config).__name__)
# datasetPtc file name (pkl)
config.datasetFileName='/project/cslage/BOT_doc/PTC_12543_R22S11/calibrations/ptc/ptcDataset-det094.pkl'

# linearizer file name (fits)
config.linearizerFileName=''

# The key by which to pull a detector from a dataId, e.g. 'ccd' or 'detector'.
config.ccdKey='detector'

# Signal value for relative systematic bias between different methods of estimating a_ij (Fig. 15 of Astier+19).
config.signalElectronsRelativeA=75000.0

# Number of bins in `plotNormalizedCovariancesNumber` function (Fig. 8, 10., of Astier+19).
config.plotNormalizedCovariancesNumberOfBins=10

