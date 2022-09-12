#!/bin/bash

set -eou pipefail

# this script will download and build the heasoft swift docker image
# it will use a ./heasoft/ directory to download files into
# after build complete, push the image with:
# docker push dresscodeswift/heasoft:"$HEASOFT_VER".swift
# visit https://heasarc.gsfc.nasa.gov/docs/software/heasoft/docker.html for more information

export DOCKER="docker"
# export DOCKER="sudo docker"

mkdir -p heasoft

# download heasoft (2.8 GB)
wget -nv -O heasoft/heasoft.tar.gz \
    "https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/tarit/tarit.pl?mode=download&arch=src&src_pc_linux_ubuntu=Y&src_other_specify=&mission=swift&general=attitude&general=caltools&general=futils&general=fimage&general=heasarc&general=heasptools&general=heatools&general=heagen&general=fv&general=timepkg&xanadu=ximage&xanadu=xronos&xanadu=xspec"

# extract
mkdir -p heasoft/heasoft_software
tar -xf heasoft/heasoft.tar.gz -C heasoft/heasoft_software --strip-components=1

# build the docker iamge
(cd heasoft/heasoft_software/Docker && make)

# extract the version number from the Makefile
HEASOFT_VER="$(awk '/^IMAGE_VERSION/ {print $3}' Docker/Makefile)"
export HEASOFT_VER

# docker tag with our dockerhub org
$DOCKER tag heasoft:"$HEASOFT_VER" dresscodeswift/heasoft:"$HEASOFT_VER".swift
