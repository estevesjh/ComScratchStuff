## Re-Runing with a change on the config file, doFlat=False, doDefect=True

# Comments
# The bias don't need to have the same filter
# The Darks don't need to have the same exposure time
echo " "
echo "Start the build calibration scripts: PTC ON"
echo " "

echo "Set Variables"
obsDate=20220217

# sef of flats w/ increasing exposure to the PTC curve 
flat_ptc0=$(printf "%05d" 200)
flat_ptc1=$(printf "%05d" 239)

echo "Starting DM Code"
echo "Observation date is: ${obsDate}"
echo " "

# Run the PTC: 
pipetask run -j 32 -d "detector IN (0..8) AND instrument='LSSTComCam' AND \
	 exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND exposure.observation_type='flat'" \
	 -b /repo/main \
	 -c isr:doFlat=False \
	 -i LSSTComCam/raw/all,LSSTComCam/calib \
	 -o u/jesteves/comcam/ptc_${obsDate}_flat \
	 -p $CP_PIPE_DIR/pipelines/LsstComCam/cpPtc.yaml \
	 --register-dataset-types

# sensors=( "S00" "S01" "S02" "S10" "S11" "S12" "S20" "S21" "S22" )
# i=0
# for Sii in "${sensors[@]}"
# do
#    :
#    echo $i
#    plotPhotonTransferCurve.py /repo/main/u/jesteves/comcam/ptc_20220217_rerun/20220506T014116Z/ptc/ptc_LSSTComCam_R22_${Sii}_u_jesteves_comcam_ptc_20220217_rerun_20220506T014116Z.fits \
#    --detNum=$i --outDir=./ptc_${obsDate}_R22_rerun/
#    i=$(($i+1))
# done

# plotPhotonTransferCurve.py \
# /repo/main/u/jesteves/comcam/ptc_20220217/20220504T150537Z/ptc/ptc_LSSTComCam_R22_${Sii}_u_jesteves_comcam_ptc_20220217_20220504T150537Z.fits \
# --detNum=1 --outDir=./ptc_${obsDate}_R22_${Sii}/