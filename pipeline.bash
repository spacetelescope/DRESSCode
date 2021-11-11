#!/bin/bash

set -e

CONFIG_FILE=config.txt

echo "1/13 Sky images part 1 (uvotimage.py)"
dc-uvotimage -c $CONFIG_FILE
echo "2/13 Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
dc-uvotskycorr -c $CONFIG_FILE
echo "3/13 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
dc-uvotattcorr -c $CONFIG_FILE
echo "4/13 Sky images part 2 (uvotimage2.py)"
dc-uvotimage2 -c $CONFIG_FILE
echo "5/13 Auxiliary files part 1, quality maps (uvotbadpix.py)"
dc-uvotbadpix -c $CONFIG_FILE
echo "6/13 Auxiliary files part 1, exposure maps (uvotexpmap.py)"
dc-uvotexpmap -c $CONFIG_FILE
echo "7/13 Aspect correction part 2 (uvotskycorr2.py)"
dc-uvotskycorr2 -c $CONFIG_FILE
echo "8/13 Auxiliary files part 2, lss maps (uvotskylss.py)"
dc-uvotskylss -c $CONFIG_FILE
echo "9/13 python sort_by_year.py"
dc-sort_by_year -c $CONFIG_FILE
echo "10/13 Summing images per observing period (uvotimsum.py)"
dc-uvotimsum -c $CONFIG_FILE
echo "11/13 Flux corrections (corrections.py)"
dc-corrections -c $CONFIG_FILE
echo "12/13 Combining the different observing periods (combine.py)"
dc-combine -c $CONFIG_FILE
echo "13/13 Calibration and aperture correction (calibration.py)"
dc-calibration -c $CONFIG_FILE

echo "FINISHED"
