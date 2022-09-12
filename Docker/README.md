# Docker

---

*DockerHub*: [hub.docker.com/dresscodeswift](https://hub.docker.com/u/dresscodeswift)

---

## Images

| Name | File path | DockerHub | Comment |
|------------|-----------|-----------|---------|
|HEASoft|[HEASoft website](https://heasarc.gsfc.nasa.gov/lheasoft/docker.html)|[heasoft ![Docker Pulls](https://img.shields.io/docker/pulls/dresscodeswift/heasoft) ![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dresscodeswift/heasoft)](https://hub.docker.com/r/dresscodeswift/heasoft)|HEASoft image from [instructions](https://heasarc.gsfc.nasa.gov/lheasoft/docker.html), with SWIFT tools|
|HEASoft w/ caldb & wcstools|[Docker/heasoft-caldb-wcstools.dockerfile](/Docker/heasoft-caldb-wcstools.dockerfile)|[heasoft-caldb-wcstools ![Docker Pulls](https://img.shields.io/docker/pulls/dresscodeswift/heasoft-caldb-wcstools) ![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dresscodeswift/heasoft-caldb-wcstools)](https://hub.docker.com/r/dresscodeswift/heasoft-caldb-wcstools)|adds `caldb` files and `wcstools`|
|dresscode|[Docker/dockerfile](/Docker/dockerfile)|[dresscode ![Docker Pulls](https://img.shields.io/docker/pulls/dresscodeswift/dresscode) ![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dresscodeswift/dresscode)](https://hub.docker.com/r/dresscodeswift/dresscode)|adds DRESSCode pipeline|

## GitHub Workflows

Compiling and building HEASoft takes a long time, so for automated testing we utilize a HEASoft docker image and install wcstools, caldb, and dresscode into that image.

We also make available the DRESSCode image with `caldb`, `wcstools`, and `dresscode` installed.

GitHub workflows build and push our docker images to dockerhub.

- [HEASoft image workflow](/.github/workflows/build_heasoft.yml)
- [DRESSCode image workflow](/.github/workflows/test-pipeline.yml) (only pushes to dockerhub on commits to `main` branch)

## Build Examples

### HEASoft Image

To build the base HEASoft image, run the [heasoft_image.sh](/Docker/heasoft_image.sh) script. 

```sh
./Docker/heasoft_image.sh
```

### caldb and wcstools image

```sh
docker build --tag dresscodeswift/heasoft-caldb-wcstools:latest -f Docker/heasoft-caldb-wcstools.dockerfile .
docker push dresscodeswift/heasoft-caldb-wcstools:latest
```

### DRESSCode Image

To build the DRESSCode image locally (tagging `latest`):

```sh
docker build --tag dresscodeswift/dresscode:latest -f Docker/dockerfile .
```

## Running pipeline from docker

The following mounts a local volume into the docker image and runs the `test_pipeline.bash` script

Adjust variables `DATA_DIR` and `GALAXY` as necessary:

```sh
DATA_DIR=/internal/work/bfalk/test_pipeline/
GALAXY=NGC0628_full
GALAXY_DIR="$DATA_DIR/$GALAXY"

cat > config.txt << END  
path = $DATA_DIR  
galaxy = $GALAXY
years = 2007, 2008, 2013, 2015
enlarge = no
add_xpix = 200
add_ypix = 100
END

GIT_TAG=$(git rev-parse --short=8 HEAD)
cp -r "$GALAXY_DIR/Raw_images" "$GALAXY_DIR/working_dir_$GIT_TAG"

docker build --tag dresscodeswift/dresscode:$GIT_TAG -f Docker/dockerfile .
docker run --rm -it \
    -v $(pwd)/config.txt:/opt/dresscode/config.txt \
    -v "$GALAXY_DIR/working_dir_$GIT_TAG":"$GALAXY_DIR/working_dir" \
    -v "$GALAXY_DIR/Raw_images":"$GALAXY_DIR/Raw_images" \
    "dresscodeswift/dresscode:$GIT_TAG" \
    /bin/bash pipeline.bash
```

Note: docker user heasoft (999:1000) must have write access to the data directories, otherwise, run w/ `--user root` in the docker run command
