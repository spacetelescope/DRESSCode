#!/bin/bash

set -e

OUTPUT_DIR=$1

# https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/swift.pl
# UVOT Log -> parameter search form
# filter: 'UVW2' OR 'UVM2' OR 'UVW1'
# pointing_mode: POINTING
# Object Name: NGC0628
# obsid's: 00032891004 OR 00032891012 OR 00035868001

echo "Downloading raw data to $OUTPUT_DIR"

for obs in "2008_02/00035868001/" "2013_08/00032891004/" "2013_08/00032891012/"
do
  echo "Downloading obs: $obs"
  wget -P "$OUTPUT_DIR" -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R "index*" -erobots=off --retr-symlinks "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/$obs"
  echo "Downloaded obs: $obs"
done

echo "Downloaded raw data"
