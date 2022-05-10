# Build the bias calibs:

# Comments
# The bias don't need to have the same filter
# The Darks don't need to have the same exposure time

echo " "
echo "Start the build calibration scripts: PTC ON"
echo " "

echo "Set Variables"
obsDate=20220505

bias0=$(printf "%05d" 60)
bias1=$(printf "%05d" 109)
dark0=$(printf "%05d" 152)
dark1=$(printf "%05d" 171)

# darks for bright defects
defect0=$(printf "%05d" 160)
defect1=$(printf "%05d" 161)

# flats for dark defects
defect2=$(printf "%05d" 255)
defect3=$(printf "%05d" 256)

# sef of flats w/ same exposure (SDSSg)
flat0=$(printf "%05d" 189)
flat1=$(printf "%05d" 210)

# sef of flats w/ increasing exposure to the PTC curve (SDSSg)
flat_ptc0=$(printf "%05d" 251)
flat_ptc1=$(printf "%05d" 290)

# # sef of flats w/ increasing exposure to the PTC curve (SDSSi)
# flat_ptc0=$(printf "%05d" 211)
# flat_ptc1=$(printf "%05d" 250)

echo "Starting DM Code"
echo "Observation date is: ${obsDate}"
echo " "

# echo "Creating Master Bias"
# echo "pipetask run -j 8 -d detector IN (0) AND exposure IN (${obsDate}${bias0}..${obsDate}${bias1}) AND instrument='LATISS'"

# pipetask run -j 8 -d "detector IN (0) AND exposure IN (${obsDate}${bias0}..${obsDate}${bias1}) \
# 	 AND instrument='LATISS' " \
# 	 -b /repo/main/butler.yaml -i LATISS/raw/all,LATISS/calib \
# 	 -o u/jesteves/latiss/bias_${obsDate} \
# 	 -p $CP_PIPE_DIR/pipelines/Latiss/cpBias.yaml --register-dataset-types

# # Ingest the bias calibs:
# butler certify-calibrations /repo/main u/jesteves/latiss/bias_${obsDate} \
#        u/jesteves/calib/latiss/bias_${obsDate} --begin-date 1980-01-01 \
#        --end-date 2050-01-01 bias

# echo "Creating Master Dark"
# # Build the dark calibs:
# pipetask run -j 8 -d "detector IN (0) AND exposure IN (${obsDate}${dark0}..${obsDate}${dark1}) \
# 	 AND instrument='LATISS' " \
# 	 -b /repo/main/butler.yaml -i LATISS/raw/all,LATISS/calib \
# 	 -o u/jesteves/latiss/dark_${obsDate} \
# 	 -p $CP_PIPE_DIR/pipelines/Latiss/cpDark.yaml \
# 	 -c isr:doDefect=False --register-dataset-types

# # Ingest the dark calibs:
# butler certify-calibrations /repo/main u/jesteves/latiss/dark_${obsDate} \
#        u/jesteves/calib/latiss/dark_${obsDate} --begin-date 1980-01-01 \
#        --end-date 2050-01-01 dark

# # Start the chained collection:
# butler collection-chain /repo/main u/jesteves/calib/latiss/calib.${obsDate} \
#        u/jesteves/calib/latiss/bias_${obsDate} \
#        u/jesteves/calib/latiss/dark_${obsDate} 

# echo "Creating Defects"
# # Build the defect calibs:
# pipetask run -j 8 -d "detector IN (0) AND exposure IN \
# 	 (${obsDate}${defect0}..${obsDate}${defect1}, ${obsDate}${defect2}..${obsDate}${defect3}) \
# 	 AND instrument='LATISS' " \
# 	 -b /repo/main/butler.yaml \
# 	 -i LATISS/raw/all,LATISS/calib,u/jesteves/calib/latiss/calib.${obsDate} \
# 	 -o u/jesteves/latiss/defects_${obsDate} \
# 	 -p $CP_PIPE_DIR/pipelines/Latiss/findDefects.yaml \
# 	 --register-dataset-types

# # Ingest the defect calibs:
# butler certify-calibrations /repo/main u/jesteves/latiss/defects_${obsDate} \
#        u/jesteves/calib/latiss/defects_${obsDate} --begin-date 1980-01-01 \
#        --end-date 2050-01-01 defects

# # Add the defects to the chained collection:

# butler collection-chain /repo/main --mode=extend \
#        u/jesteves/calib/latiss/calib.${obsDate} \
#        u/jesteves/calib/latiss/defects_${obsDate}

# echo "Creating Master Flat"
# # Build the flat calibs:
# pipetask run -j 8 -d "detector IN (0) AND exposure IN (${obsDate}${flat0}..${obsDate}${flat1}) \
# 	 AND instrument='LATISS' " \
# 	 -b /repo/main/butler.yaml \
# 	 -i LATISS/raw/all,LATISS/calib,u/jesteves/calib/latiss/calib.${obsDate} \
# 	 -o u/jesteves/latiss/flat_${obsDate} \
# 	 -p $CP_PIPE_DIR/pipelines/Latiss/cpFlat.yaml --register-dataset-types

# # Ingest the flat calibs:

# butler certify-calibrations /repo/main u/jesteves/latiss/flat_${obsDate} \
#        u/jesteves/calib/latiss/flat_${obsDate} --begin-date 1980-01-01 \
#        --end-date 2050-01-01 flat

# # Add the flat to the chained collection:

# butler collection-chain /repo/main --mode=extend \
#        u/jesteves/calib/latiss/calib.${obsDate} \
#        u/jesteves/calib/latiss/flat_${obsDate} 

echo "Creating PTC Curves"
echo "exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND exposure.observation_type='flat'"

# Run the PTC: 
pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND \
	 exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND exposure.observation_type='flat'" \
	 -b /repo/main \
     -c isr:doFlat=False \
     -i LATISS/raw/all,LATISS/calib,LATISS/calib,u/jesteves/calib/latiss/calib.${obsDate} \
	 -o u/jesteves/latiss/ptc_${obsDate}_flat \
	 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml \
	 --register-dataset-types

echo "PTC collection: u/jesteves/latiss/ptc_${obsDate}" 
echo "Congrats ! It's Done"

# Plot the PTC:

# plotPhotonTransferCurve.py \ /repo/main/u/jesteves/latiss/ptc_20220505/20220506T011002Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220505_20220506T011002Z.fits \
# --detNum=0 --outDir=./
# plotPhotonTransferCurve.py /repo/main/u/jesteves/latiss/ptc_20220505_SDSSi/20220506T014156Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220505_SDSSi_20220506T014156Z.fits --detNum=0 --outDir=./

# plotPhotonTransferCurve.py /repo/main/u/jesteves/latiss/ptc_20220405/20220408T211458Z/ptc/ptc_LATISS_RXX_S00_u_jesteves_latiss_ptc_20220405_20220408T211458Z.fits --detNum=0 --outDir=./

# ## look for exposures
# obsDate=20220504
# butler query-dimension-records /repo/main exposure --where "instrument='LATISS' AND exposure.observation_type='flat' AND exposure.day_obs > $((obsDate-1)) AND exposure.day_obs <$((obsDate+1))"