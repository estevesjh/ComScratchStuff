#!/usr/bin/env bash
echo "Run 20 pairs for the days between 24 Feb 2022 and 04 May 2022"

pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND exposure IN (2022022400046, 2022022400047, 2022022400048, 2022022400049, 2022022400052, 2022022400053, 2022022400054, 2022022400055, 2022022400062, 2022022400063, 2022022400064, 2022022400065, 2022022400066, 2022022400067, 2022022400068, 2022022400069) AND exposure.observation_type='flat'" -b /repo/main -c isr:doFlat=False -i LATISS/raw/all,LATISS/calib,LATISS/calib -o u/jesteves/latiss/ptc_tREB_rerun_20220224 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs --register-dataset-types


pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND exposure IN (2022040500093, 2022040500094, 2022040500095, 2022040500096, 2022040500131, 2022040500132) AND exposure.observation_type='flat'" -b /repo/main -c isr:doFlat=False -i LATISS/raw/all,LATISS/calib,LATISS/calib -o u/jesteves/latiss/ptc_tREB_rerun_20220405 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs --register-dataset-types


pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND exposure IN (2022040600140, 2022040600141, 2022040600142, 2022040600143, 2022040600144, 2022040600145) AND exposure.observation_type='flat'" -b /repo/main -c isr:doFlat=False -i LATISS/raw/all,LATISS/calib,LATISS/calib -o u/jesteves/latiss/ptc_tREB_rerun_20220406 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs --register-dataset-types


pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND exposure IN (2022050300095, 2022050300096, 2022050300097, 2022050300098) AND exposure.observation_type='flat'" -b /repo/main -c isr:doFlat=False -i LATISS/raw/all,LATISS/calib,LATISS/calib -o u/jesteves/latiss/ptc_tREB_rerun_20220503 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs --register-dataset-types


pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND exposure IN (2022050400136, 2022050400137, 2022050400138, 2022050400139) AND exposure.observation_type='flat'" -b /repo/main -c isr:doFlat=False -i LATISS/raw/all,LATISS/calib,LATISS/calib -o u/jesteves/latiss/ptc_tREB_rerun_20220504 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs --register-dataset-types


pipetask run -j 32 -d "detector IN (0) AND instrument='LATISS' AND exposure IN (2022050500134, 2022050500135, 2022050500253, 2022050500254) AND exposure.observation_type='flat'" -b /repo/main -c isr:doFlat=False -i LATISS/raw/all,LATISS/calib,LATISS/calib -o u/jesteves/latiss/ptc_tREB_rerun_20220505 -p $CP_PIPE_DIR/pipelines/Latiss/cpPtc.yaml#gainFromFlatPairs --register-dataset-types
