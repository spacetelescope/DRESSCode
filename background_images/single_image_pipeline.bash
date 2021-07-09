#!/bin/bash

set -e

DRESSCODE_INSTALL=$1
DATA_DIR=$2
OBS=${3:-"2009_03/00030810060"}
GALAXY=${OBS////_}  # replace slashes with underscores
OUTPUT_DIR="$DATA_DIR/$GALAXY/Raw_data"

echo "DRESSCODE_INSTALL: $DRESSCODE_INSTALL"
echo "DATA_DIR: $DATA_DIR"
echo "OUTPUT_DIR: $OUTPUT_DIR"

# either pass in an observation or it uses a default: 2009_03/00030810060

mkdir -p "$OUTPUT_DIR"
wget -P "$OUTPUT_DIR" -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks http://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"$OBS"/

file="$DRESSCODE_INSTALL/config.txt"
{
    echo "path = $DATA_DIR/"
    echo "galaxy = $GALAXY"
    echo "years = 2009"
    echo "enlarge = yes"
    echo "add_xpix = 250"
    echo "add_ypix = 200"
} > $file

cd $DRESSCODE_INSTALL

# rearranging files into Raw_images directory
if [ -d $DATA_DIR/$GALAXY/Raw_images/ ]
then
    rm -r $DATA_DIR/$GALAXY/Raw_images/*
    rmdir $DATA_DIR/$GALAXY/Raw_images
fi

python collect_images.py

gunzip $DATA_DIR/$GALAXY/Raw_images/*.gz

# copy Raw_images to working_dir
if [ -d $DATA_DIR/$GALAXY/working_dir/ ]
then
    rm -r $DATA_DIR/$GALAXY/working_dir/*
    rmdir $DATA_DIR/$GALAXY/working_dir
fi
cp -r $DATA_DIR/$GALAXY/Raw_images $DATA_DIR/$GALAXY/working_dir

echo "1/13 Sky images part 1 (uvotimage.py)"
python uvotimage.py

echo "2/13 Aspect correction part 1, calc aspect correction (uvotskycorr.py)"
python uvotskycorr.py

echo "3/13 Aspect correction part 1, adjust attitude files w/ calc. aspect corrections (uvotattcorr.py)"
python uvotattcorr.py
