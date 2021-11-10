#!/bin/bash

set -e

echo "1/13 Sky images part 1 (uvotimage.py)"
uvotimage
echo "2/13 Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
uvotskycorr
echo "3/13 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
uvotattcorr
echo "4/13 Sky images part 2 (uvotimage2.py)"
uvotimage2
echo "5/13 Auxiliary files part 1, quality maps (uvotbadpix.py)"
uvotbadpix
echo "6/13 Auxiliary files part 1, exposure maps (uvotexpmap.py)"
uvotexpmap
echo "7/13 Aspect correction part 2 (uvotskycorr2.py)"
uvotskycorr2
echo "8/13 Auxiliary files part 2, lss maps (uvotskylss.py)"
uvotskylss
echo "9/13 python sort_by_year.py"
sort_by_year
echo "10/13 Summing images per observing period (uvotimsum.py)"
uvotimsum
echo "11/13 Flux corrections (corrections.py)"
corrections
echo "12/13 Combining the different observing periods (combine.py)"
combine
echo "13/13 Calibration and aperture correction (calibration.py)"
calibration

echo "FINISHED"
