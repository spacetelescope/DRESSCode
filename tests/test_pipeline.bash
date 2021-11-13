#!/bin/bash

set -e

# this bash script runs the pipeline, assumes test data already downloaded

# if running as another user (e.g. root), need to source the venv
source /home/heasoft/venv/bin/activate

CUR_DIR=$(PWD)

# creating data directories
# if user specifies a data directory, we use that here, otherwise we use home directory
if [ $# -eq 1 ]
then
    cd $1
    DATA_DIR=$(pwd)
    echo "Data volume location specified using: $DATA_DIR"
else
    mkdir -p ~/dresscode-data/
    cd ~/dresscode-data
    DATA_DIR=$(pwd)
    echo "No data volume location specified, using: $DATA_DIR"
fi
GALAXY="NGC0628"

cd $CUR_DIR

# creating config.txt
file="$CUR_DIR/config.txt"
{
    echo "path = $DATA_DIR/"
    echo "galaxy = $GALAXY"
    echo "years = 2008, 2013"
    echo "enlarge = yes"
    echo "add_xpix = 250"
    echo "add_ypix = 200"
} > "$file"

# rearranging files into Raw_images directory
if [ -d "$DATA_DIR/$GALAXY/Raw_images/" ]
then
    rm -rf "$DATA_DIR/$GALAXY/Raw_images"
fi

dc-collect_images -c config.txt

# uncompress Raw_images
gunzip $DATA_DIR/$GALAXY/Raw_images/*.gz

# copy Raw_images to working_dir
if [ -d "$DATA_DIR/$GALAXY/working_dir/" ]
then
    rm -rf "$DATA_DIR/$GALAXY/working_dir"
fi
cp -r "$DATA_DIR/$GALAXY/Raw_images" "$DATA_DIR/$GALAXY/working_dir"

# run the pipeline
echo "Running the pipeline"
bash pipeline.bash
