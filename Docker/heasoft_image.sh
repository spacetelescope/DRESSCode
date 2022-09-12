#!/bin/bash

set -eou pipefail

# this script downloads and builds the heasoft SWIFT docker image
# it will use a ./heasoft_{DATE}/ directory as a working directory
# after docker build is complete, push the image with:
# docker push dresscodeswift/heasoft:"$HEASOFT_VER".swift
# See your pushed image at https://hub.docker.com/repository/docker/dresscodeswift/heasoft

# For heasoft docker instructions visit
# https://heasarc.gsfc.nasa.gov/docs/software/heasoft/docker.html

# some installations of docker require `sudo`
export DOCKER="docker"
# export DOCKER="sudo docker"

# create a unique workdir
WORKDIR="heasoft_$(date '+%FT%H-%M-%S')"
mkdir -p "$WORKDIR"

# download heasoft (2.8 GB)
wget -nv -O "$WORKDIR"/heasoft.tar.gz \
    "https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/tarit/tarit.pl?mode=download&arch=src&src_pc_linux_ubuntu=Y&src_other_specify=&mission=swift&general=attitude&general=caltools&general=futils&general=fimage&general=heasarc&general=heasptools&general=heatools&general=heagen&general=fv&general=timepkg&xanadu=ximage&xanadu=xronos&xanadu=xspec"

# extract
tar -xf "$WORKDIR"/heasoft.tar.gz -C "$WORKDIR"

# extract the version number from the heasoft directory name
HEASOFT_VER=$(find "$WORKDIR" -mindepth 1 -maxdepth 1 -type d | sed -r "s/$WORKDIR\/heasoft-(.*)$/\1/")
export HEASOFT_VER

# build the docker iamge
(cd "$WORKDIR"/heasoft-"$HEASOFT_VER"/Docker && make)

# docker tag with dresscode organization
$DOCKER tag heasoft:"$HEASOFT_VER" dresscodeswift/heasoft:"$HEASOFT_VER".swift
