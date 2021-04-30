set -e

echo "Sky images part 1 (uvotimage.py)"
python uvotimage.py
echo "Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
python uvotskycorr.py
echo "Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
python uvotattcorr.py
echo "Sky images part 2 (uvotimage2.py)"
python uvotimage2.py
echo "Auxiliary files part 1, quality maps (uvotbadpix.py)"
python uvotbadpix.py
echo "Auxiliary files part 1, exposure maps (uvotexpmap.py)"
python uvotexpmap.py
echo "Aspect correction part 2 (uvotskycorr2.py)"
python uvotskycorr2.py
echo "Auxiliary files part 2, lss maps (uvotskylss.py)"
python uvotskylss.py
echo "python sort_by_year.py"
python sort_by_year.py
echo "Summing images per observing period (uvotimsum.py)"
python uvotimsum.py
echo "Flux corrections (corrections.py)"
python corrections.py
echo "Combining the different observing periods (combine.py)"
python combine.py
echo "Calibration and aperture correction (calibration.py)"
python calibration.py
