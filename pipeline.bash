#!/bin/bash

set -e

CONFIG_FILE=config.txt

echo "1/13 Sky images part 1 (uvotimage.py)"
uvotimage -c $CONFIG_FILE
echo "2/13 Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
uvotskycorr -c $CONFIG_FILE
echo "3/13 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
uvotattcorr -c $CONFIG_FILE
echo "4/13 Sky images part 2 (uvotimage2.py)"
uvotimage2 -c $CONFIG_FILE
echo "5/13 Auxiliary files part 1, quality maps (uvotbadpix.py)"
uvotbadpix -c $CONFIG_FILE
echo "6/13 Auxiliary files part 1, exposure maps (uvotexpmap.py)"
uvotexpmap -c $CONFIG_FILE
echo "7/13 Aspect correction part 2 (uvotskycorr2.py)"
uvotskycorr2 -c $CONFIG_FILE
echo "8/13 Auxiliary files part 2, lss maps (uvotskylss.py)"
uvotskylss -c $CONFIG_FILE
echo "9/13 python sort_by_year.py"
sort_by_year -c $CONFIG_FILE
echo "10/13 Summing images per observing period (uvotimsum.py)"
uvotimsum -c $CONFIG_FILE
echo "11/13 Flux corrections (corrections.py)"
corrections -c $CONFIG_FILE
echo "12/13 Combining the different observing periods (combine.py)"
combine -c $CONFIG_FILE
echo "13/13 Calibration and aperture correction (calibration.py)"
calibration -c $CONFIG_FILE

echo "FINISHED"
