#!/bin/bash

set -e

CONFIG_FILE=config.txt

echo "01/11 Sky images part 1 (uvotimage.py)"
dc-uvotimage -c $CONFIG_FILE
echo "02/11 Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
dc-uvotskycorr -c $CONFIG_FILE
echo "03/11 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
dc-uvotattcorr -c $CONFIG_FILE
echo "04/11 Sky images part 2 (uvotimage2.py)"
dc-uvotimage2 -c $CONFIG_FILE
echo "05/11 Auxiliary files part 1, quality maps (uvotbadpix.py)"
dc-uvotbadpix -c $CONFIG_FILE
echo "06/11 Auxiliary files part 1, exposure maps (uvotexpmap.py)"
dc-uvotexpmap -c $CONFIG_FILE
echo "07/11 Aspect correction part 2 (uvotskycorr2.py)"
dc-uvotskycorr2 -c $CONFIG_FILE
echo "08/11 Auxiliary files part 2, large scale sensitivity maps (uvotskylss.py)"
dc-uvotskylss -c $CONFIG_FILE
echo "09/11 Flux corrections (corrections.py)"
dc-corrections -c $CONFIG_FILE
echo "10/11 Summing images per observing period (uvotimsum.py)"
dc-uvotimsum -c $CONFIG_FILE
echo "11/11 Calibration and aperture correction (calibration.py)"
dc-calibration -c $CONFIG_FILE

echo "FINISHED"
