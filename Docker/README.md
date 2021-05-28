# Docker

Docker organization: [dresscodeswift](https://hub.docker.com/repository/docker/dresscodeswift)

## Images

| Name | File path | DockerHub | Comment |
|------------|-----------|-----------|---------|
|heasoft|[Heasoft website](https://heasarc.gsfc.nasa.gov/lheasoft/docker.html)|[dresscodeswift/heasoft](https://hub.docker.com/repository/docker/dresscodeswift/heasoft)|base heasoft image built from their [instructions](https://heasarc.gsfc.nasa.gov/lheasoft/docker.html), with SWIFT tools|
|heasoft w/ caldb & wcstools|[Docker/heasoft-caldb-wcstools.dockerfile](/Docker/heasoft-caldb-wcstools.dockerfile)|[dresscodeswift/heasoft-caldb-wcstools](https://hub.docker.com/repository/docker/dresscodeswift/heasoft-caldb-wcstools)|         |
|dresscode|[Docker/dockerfile](/Docker/dockerfile)|[dresscodeswift/dresscode](https://hub.docker.com/repository/docker/dresscodeswift/dresscode)|for end users|

## GitHub Actions

Todo

- push docker image on merge to `main` branch
- testing (WIP)

## Testing

The following mounts a local volume into the docker image and runs the `test_pipeline.bash` script

```sh
docker run --rm -it -v ~/dresscode-data/:/data/dresscode-data \
    dresscodeswift/dresscode \
    /bin/bash /opt/dresscode/tests/test_pipeline.bash /opt/dresscode /data/dresscode-data 
```
