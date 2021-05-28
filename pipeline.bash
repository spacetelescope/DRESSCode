#!/bin/bash

set -e

echo "1/13 Sky images part 1 (uvotimage.py)"
python uvotimage.py
echo "2/13 Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
python uvotskycorr.py
echo "3/13 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
python uvotattcorr.py
echo "4/13 Sky images part 2 (uvotimage2.py)"
python uvotimage2.py
echo "5/13 Auxiliary files part 1, quality maps (uvotbadpix.py)"
python uvotbadpix.py
echo "6/13 Auxiliary files part 1, exposure maps (uvotexpmap.py)"
python uvotexpmap.py
echo "7/13 Aspect correction part 2 (uvotskycorr2.py)"
python uvotskycorr2.py
echo "8/13 Auxiliary files part 2, lss maps (uvotskylss.py)"
python uvotskylss.py
echo "9/13 python sort_by_year.py"
python sort_by_year.py
echo "10/13 Summing images per observing period (uvotimsum.py)"
python uvotimsum.py
echo "11/13 Flux corrections (corrections.py)"
python corrections.py
echo "12/13 Combining the different observing periods (combine.py)"
python combine.py
echo "13/13 Calibration and aperture correction (calibration.py)"
python calibration.py

echo "FINISHED"
