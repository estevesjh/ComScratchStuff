# Build the bias calibs:

# Comments
# The bias don't need to have the same filter
# The Darks don't need to have the same exposure time

echo " "
echo "Start the build calibration scripts: PTC ON"
echo " "

echo "Set Variables"
obsDate=20220922

bias0=$(printf "%05d" 32)
bias1=$(printf "%05d" 51)

# dark0=$(printf "%05d" 52)
# dark1=$(printf "%05d" 71)

# darks for bright defects
defect0=$(printf "%05d" 55)
defect1=$(printf "%05d" 57)

# flats for dark defects
defect2=$(printf "%05d" 102)
defect3=$(printf "%05d" 103)

# sef of flats w/ same exposure (Empty)
# flat0=$(printf "%05d" None)
# flat1=$(printf "%05d" None)

# sef of flats w/ increasing exposure to the PTC curve (Empty)
flat_ptc0=$(printf "%05d" 72)
flat_ptc1=$(printf "%05d" 103)

#repo="LATISS"
repo="/sdf/group/rubin/repo/oga"
jesteves="u/esteves/sdf"
# jesteves="u/jesteves"

echo "Starting DM Code"
echo "Observation date is: ${obsDate}"
echo " "

echo "Creating Master Bias"
echo "pipetask run -j 8 -d detector IN (0) AND exposure IN (${obsDate}${bias0}..${obsDate}${bias1}) AND instrument='LATISS'"

pipetask run -j 12 -d "detector IN (0) AND exposure IN (${obsDate}${bias0}..${obsDate}${bias1}) \
	 AND instrument='LATISS' " \
	 -b ${repo}/butler.yaml -i LATISS/raw/all,LATISS/calib \
	 -o ${jesteves}/latiss/bias_${obsDate} \
	 -p $CP_PIPE_DIR/pipelines/Latiss/cpBias.yaml --register-dataset-types

# Ingest the bias calibs:
echo "Ingest Bias Calibs"
echo "butler certify-calibrations $repo ${jesteves}/latiss/bias_${obsDate} \
       ${jesteves}/calib/latiss/bias_${obsDate} --begin-date 1980-01-01 \
       --end-date 2050-01-01 bias
"
butler certify-calibrations $repo ${jesteves}/latiss/bias_${obsDate} \
       ${jesteves}/calib/latiss/bias_${obsDate} --begin-date 1980-01-01 \
       --end-date 2050-01-01 bias

echo "Start Chained Collection"
butler collection-chain $repo ${jesteves}/calib/latiss/calib.${obsDate} \
       ${jesteves}/calib/latiss/bias_${obsDate} 
       # ${jesteves}/calib/latiss/dark_${obsDate} 

echo "Creating Defects"
# Build the defect calibs:
pipetask run -j 8 -d "detector IN (0) AND exposure IN \
	 (${obsDate}${defect0}..${obsDate}${defect1}, ${obsDate}${defect2}..${obsDate}${defect3}) \
	 AND instrument='LATISS' " \
	 -b ${repo}/butler.yaml \
	 -i LATISS/raw/all,LATISS/calib, ${jesteves}/calib/latiss/calib.${obsDate} \
	 -o ${jesteves}/latiss/defects_${obsDate} \
	 -p $CP_PIPE_DIR/pipelines/Latiss/findDefects.yaml \
	 --register-dataset-types

# Ingest the defect calibs:
echo "Ingest the defect calibs"
butler certify-calibrations $repo ${jesteves}/latiss/defects_${obsDate} \
       ${jesteves}/calib/latiss/defects_${obsDate} --begin-date 1980-01-01 \
       --end-date 2050-01-01 defects

# # # Add the defects to the chained collection:

echo "Add the defects to the chained collection"
butler collection-chain $repo --mode=extend \
       ${jesteves}/calib/latiss/calib.${obsDate} \
       ${jesteves}/calib/latiss/defects_${obsDate}

echo "Creating PTC Curves"
echo "exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND exposure.observation_type='flat'"

# Run the PTC: 
pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND \
	 exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND exposure.observation_type='flat'" \
	 -b $repo \
     -c isr:doFlat=False \
     -i LATISS/raw/all,LATISS/calib,${jesteves}/calib/latiss/calib.${obsDate} \
	 -o ${jesteves}/latiss/ptc_${obsDate} \
	 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml \
	 --register-dataset-types

echo "PTC collection: ${jesteves}/latiss/ptc_${obsDate}" 
echo "Congrats ! It's Done"

# # Plot the PTC:

plotPhotonTransferCurve.py \ /sdf/group/rubin/repo/main/u/jesteves/latiss/ptc_20220504_flat/20220506T074230Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220504_flat_20220506T074230Z.fits \
 --detNum=0 --outDir=./
 
# # plotPhotonTransferCurve.py \ /repo/main/u/jesteves/latiss/ptc_20220505/20220506T011002Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220505_20220506T011002Z.fits \
# # --detNum=0 --outDir=./
# # plotPhotonTransferCurve.py /repo/main/u/jesteves/latiss/ptc_20220505_SDSSi/20220506T014156Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220505_SDSSi_20220506T014156Z.fits --detNum=0 --outDir=./

# # plotPhotonTransferCurve.py /repo/main/u/jesteves/latiss/ptc_20220405/20220408T211458Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220405_20220408T211458Z.fits --detNum=0 --outDir=./

# # ## look for exposures
# # obsDate=20220504
# # butler query-dimension-records /repo/main exposure --where "instrument='LATISS' AND exposure.observation_type='flat' AND exposure.day_obs > $((obsDate-1)) AND exposure.day_obs <$((obsDate+1))"
