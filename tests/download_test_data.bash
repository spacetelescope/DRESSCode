#!/bin/bash

set -e

OUTPUT_DIR=$1

# https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/swift.pl
# parameter search form
# filter: 'UVW2' OR 'UVM2' OR 'UVW1'
# pointing_mode: POINTING
# Object Name: NGC0628
# obsid's: 00032891001;00032891019;00035868001;00036568001;00036568002;00036568003

echo "Downloading raw data to $OUTPUT_DIR"

for obs in "2007_07/00036568001/" "2008_02/00035868001/" "2015_06/00036568002/" "2013_07/00032891001/" "2013_08/00032891019/" "2015_07/00036568003/"
do
  echo "Downloading obs: $obs"
  wget -P "$OUTPUT_DIR" -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R "index*" -erobots=off --retr-symlinks "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/$obs"
  echo "Downloaded obs: $obs"
done

echo "Downloaded raw data"
