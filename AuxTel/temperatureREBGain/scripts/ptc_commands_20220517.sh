#!/usr/bin/env bash
## Re-Runing with a change on the config file, doFlat=False, doDefect=True

# Comments
# The bias don't need to have the same filter
# The Darks don't need to have the same exposure time
echo " "
echo "Start the build calibration scripts: PTC ON"
echo " "

declare -A obsDates
declare -A flat_ptc_a
declare -A flat_ptc_b

# obsDates[0]=20220502
# flat_ptc_a[0]=$(printf "%05d" 26)
# flat_ptc_b[0]=$(printf "%05d" 27)

# obsDates[1]=20220407
# flat_ptc_a[1]=$(printf "%05d" 48)
# flat_ptc_b[1]=$(printf "%05d" 47)

# obsDates[2]=20220406
# flat_ptc_a[2]=$(printf "%05d" 206)
# flat_ptc_b[2]=$(printf "%05d" 245)

# obsDates[3]=20220405
# flat_ptc_a[3]=$(printf "%05d" 131)
# flat_ptc_b[3]=$(printf "%05d" 170)

# obsDates[4]=20220317
# flat_ptc_a[4]=$(printf "%05d" 118)
# flat_ptc_b[4]=$(printf "%05d" 158)

# obsDates[5]=20220316
# flat_ptc_a[5]=$(printf "%05d" 179)
# flat_ptc_b[5]=$(printf "%05d" 212)

# get length of an array
length=${#obsDates[@]}
 
# use C style for loop syntax to read all values and indexes
for (( j=0; j<length; j++ ));
do
  obsDate=${obsDates[$j]}
  flat_ptc0=${flat_ptc_a[$j]}
  flat_ptc1=${flat_ptc_b[$j]}
  printf "Current index %d: %s\n" $j "${obsDate}, ${flat_ptc0}, ${flat_ptc1}"
  # Run the PTC: 
  pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND \
       exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND   exposure.observation_type='flat'" \
       -b /repo/main \
       -c isr:doFlat=False \
       -i LATISS/raw/all,LATISS/calib,LATISS/calib \
       -o u/jesteves/latiss/ptc_tREB_${obsDate} \
       -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs \
       --register-dataset-types
done


obsDate=20220407
flat_ptc0=$(printf "%05d" 48)
flat_ptc1=$(printf "%05d" 47)

obsDate=20220317
flat_ptc0=$(printf "%05d" 118)
flat_ptc1=$(printf "%05d" 122)

obsDate=20220316
flat_ptc0=$(printf "%05d" 179)
flat_ptc1=$(printf "%05d" 181)

pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND \
   exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND   exposure.observation_type='flat'" \
   -b /repo/main \
   -c isr:doFlat=False \
   -i LATISS/raw/all,LATISS/calib,LATISS/calib \
   -o u/jesteves/latiss/ptc_tREB_${obsDate} \
   -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs \
   --register-dataset-types

# echo "Starting DM Code"
# echo "Observation date is: ${obsDate}"
# echo " "

# echo "Set Variables"
# obsDate=20220407

# # sef of flats w/ increasing exposure to the PTC curve 
# flat_ptc0=$(printf "%05d" 48)
# flat_ptc1=$(printf "%05d" 87)

# echo "Starting DM Code"
# echo "Observation date is: ${obsDate}"
# echo " "

# # Run the PTC: 
# pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND \
#      exposure IN (${obsDate}${flat_ptc0}..${obsDate}${flat_ptc1}) AND exposure.observation_type='flat'" \
#      -b /repo/main \
#      -c isr:doFlat=False \
#      -i LATISS/raw/all,LATISS/calib,LATISS/calib \
# 	 -o u/jesteves/latiss/ptc_tREB \
#      -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs \
#      --register-dataset-types


git clone https://github.com/lsst-sitcom/summit_extras.git
cd summit_extras
setup -j -r .
scons -j 4