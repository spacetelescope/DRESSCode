# Docker

---

*DockerHub*: [hub.docker.com/dresscodeswift](https://hub.docker.com/u/dresscodeswift)

---

## Images

| Name | File path | DockerHub | Comment |
|------------|-----------|-----------|---------|
|heasoft|[Heasoft website](https://heasarc.gsfc.nasa.gov/lheasoft/docker.html)|[heasoft ![Docker Pulls](https://img.shields.io/docker/pulls/dresscodeswift/heasoft) ![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dresscodeswift/heasoft)](https://hub.docker.com/repository/docker/dresscodeswift/heasoft)|heasoft image from [instructions](https://heasarc.gsfc.nasa.gov/lheasoft/docker.html), with SWIFT tools|
|heasoft w/ caldb & wcstools|[Docker/heasoft-caldb-wcstools.dockerfile](/Docker/heasoft-caldb-wcstools.dockerfile)|[heasoft-caldb-wcstools ![Docker Pulls](https://img.shields.io/docker/pulls/dresscodeswift/heasoft-caldb-wcstools) ![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dresscodeswift/heasoft-caldb-wcstools)](https://hub.docker.com/repository/docker/dresscodeswift/heasoft-caldb-wcstools)|adds caldb files and wcstools|
|dresscode|[Docker/dockerfile](/Docker/dockerfile)|[dresscode ![Docker Pulls](https://img.shields.io/docker/pulls/dresscodeswift/dresscode) ![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dresscodeswift/dresscode)](https://hub.docker.com/repository/docker/dresscodeswift/dresscode)|adds DRESSCode pipeline|

## GitHub Actions

- [push docker image on merge to `main` branch](/.github/workflows/main.yml)
- [testing (WIP)](/.github/workflows/test-pipeline.yml)

## Testing

The following mounts a local volume into the docker image and runs the `test_pipeline.bash` script

```sh
docker run --rm -it -v ~/dresscode-data/:/data \
    dresscodeswift/dresscode \
    /bin/bash /opt/dresscode/tests/test_pipeline.bash /opt/dresscode /data
```

## Build and push dependency docker image

```sh
docker build --tag dresscodeswift/heasoft-caldb-wcstools:latest -f Docker/heasoft-caldb-wcstools.dockerfile .
docker push dresscodeswift/heasoft-caldb-wcstools:latest
```

To build the base heasoft image, follow the Heasoft Docker [instructions](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/docker.html).

## DRESSCode Image

To build the DRESSCode image locally:

```sh
docker build --tag dresscodeswift/dresscode:latest -f Docker/dockerfile .
```
