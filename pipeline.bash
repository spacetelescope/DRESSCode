#!/bin/bash

set -e

CONFIG_FILE=config.txt

echo "Dresscode: 01/11 Sky images part 1 (dc-uvotimage)"
dc-uvotimage -c $CONFIG_FILE
echo "Dresscode: 02/11 Aspect correction part 1, calc aspect correction (dc-uvotskycorr)"
dc-uvotskycorr -c $CONFIG_FILE
echo "Dresscode: 03/11 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (dc-uvotattcorr)"
dc-uvotattcorr -c $CONFIG_FILE
echo "Dresscode: 04/11 Sky images part 2 (dc-uvotimage2)"
dc-uvotimage2 -c $CONFIG_FILE
echo "Dresscode: 05/11 Auxiliary files part 1, quality maps (dc-uvotbadpix)"
dc-uvotbadpix -c $CONFIG_FILE
echo "Dresscode: 06/11 Auxiliary files part 1, exposure maps (dc-uvotexpmap)"
dc-uvotexpmap -c $CONFIG_FILE
echo "Dresscode: 07/11 Aspect correction part 2 (dc-uvotskycorr2)"
dc-uvotskycorr2 -c $CONFIG_FILE
echo "Dresscode: 08/11 Auxiliary files part 2, lss maps (dc-uvotskylss)"
dc-uvotskylss -c $CONFIG_FILE
echo "Dresscode: 09/11 Flux corrections (dc-corrections)"
dc-corrections -c $CONFIG_FILE
echo "Dresscode: 10/11 Summing images per observing period (dc-uvotimsum)"
dc-uvotimsum -c $CONFIG_FILE
echo "Dresscode: 11/11 Calibration and aperture correction (dc-calibration)"
dc-calibration -c $CONFIG_FILE

echo "FINISHED"
