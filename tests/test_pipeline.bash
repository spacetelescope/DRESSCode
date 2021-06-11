#!/bin/bash

set -e

# this bash script runs the pipeline, assumes test data already downloaded

# if running as another user, need to source the venv
source /home/heasoft/venv/bin/activate

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

# creating config.txt

file="$DRESSCODE_INSTALL/config.txt"
echo "path = $DATA_DIR/" > $file
echo "galaxy = $GALAXY" >> $file
echo "years = 2008, 2013" >> $file
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