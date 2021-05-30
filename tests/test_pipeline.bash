#!/bin/bash

set -e

# this bash script pulls down some test data and then runs the pipeline

# set dresscode install location if specified as argument, otherwise use current directory
if [ $# -eq 0 ]
then
    echo "Dresscode installation not specified, using current environment: $PWD"
    DRESSCODE_INSTALL=$PWD
else
    DRESSCODE_INSTALL=$1
fi

# creating data directories
# if users specifies a data directory, we use that here, otherwise we use home directory
if [ $# -eq 2 ]
then
    cd $2
    DATA_DIR=$(pwd)
    echo "Data volume location specified using: $DATA_DIR"
else
    mkdir -p ~/dresscode-data/
    cd ~/dresscode-data
    DATA_DIR=$(pwd)
    echo "No data volume location specified, using: $DATA_DIR"
fi
GALAXY="NGC0628"
mkdir -p $DATA_DIR/$GALAXY/Raw_data
cd $DATA_DIR/$GALAXY/Raw_data

# downloading test files
echo "Downloading test files to: $(pwd)"

# https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/swift.pl
# parameter search form
# filter: 'UVW2' OR 'UVM2' OR 'UVW1'
# pointing_mode: POINTING
# Object Name: NGC0628
# obsid's: 00032891001;00032891019;00035868001;00036568001;00036568002;00036568003

wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/2007_07//00036568001/
wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/2008_02//00035868001/
wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/2015_06//00036568002/
wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/2013_07//00032891001/
wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/2013_08//00032891019/
wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/2015_07//00036568003/

# creating config.txt

file="$DRESSCODE_INSTALL/config.txt"
echo "path = $DATA_DIR/" > $file
echo "galaxy = $GALAXY" >> $file
echo "years = 2007, 2008, 2013, 2015" >> $file
echo "enlarge = no" >> $file
echo "add_xpix = 200" >> $file
echo "add_ypix = 100" >> $file

# change directory to dresscode install
cd $DRESSCODE_INSTALL

# rearranging files into Raw_images directory
if [ -d $DATA_DIR/$GALAXY/Raw_images/ ]
then
    rm -r $DATA_DIR/$GALAXY/Raw_images/*
    rmdir $DATA_DIR/$GALAXY/Raw_images
fi
python collect_images.py

# uncompress Raw_images
gunzip $DATA_DIR/$GALAXY/Raw_images/*.gz

# copy Raw_images to working_dir
if [ -d $DATA_DIR/$GALAXY/working_dir/ ]
then
    rm -r $DATA_DIR/$GALAXY/working_dir/*
    rmdir $DATA_DIR/$GALAXY/working_dir
fi
cp -r $DATA_DIR/$GALAXY/Raw_images $DATA_DIR/$GALAXY/working_dir

# run the pipeline
echo "Running the pipeline"
bash pipeline.bash