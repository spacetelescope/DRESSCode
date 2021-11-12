# Installation Instructions

## Docker Installation

Docker can be used to run the software without having to complete the heasoft/caldb/wcstools installation procedure yourself (or to run on windows). The image can be found on [docker hub](https://hub.docker.com/r/dresscodeswift/dresscode). It also includes the latest version of the DRESSCode pipeline, along with any other python dependencies.

To download and open an interactive shell with the prerequisites already installed:

```sh
docker pull dresscodeswift/dresscode
docker run --rm -it dresscodeswift/dresscode /bin/bash
```

From there run the pipeline, which is located in `/opt/dresscode`

You will probably want to download the data onto a persistent volume. For this, see <a href="https://docs.docker.com/storage/volumes/" target="_blank">docker documentation</a>.

## Local Installation

The following steps will install Heasoft, caldb, and wcstools on your machine

### Download Heasoft software

- Go to <https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/download.html>
- STEP 1
    - Select the type of software: Choose "SOURCE CODE DISTRIBUTION"
    - Choose your platform, e.g. "PC - Ubuntu Linux 20.04"
- STEP 2
    - Download the desired packages: Select the "Swift" mission (all FTOOLS and XANADU will automatically be selected)
- Submit and wait
- Untar the file

### Install/Build Heasoft software

- STEP 3 - Install the software: Follow the installation guide for your platform, e.g. "PC Linux - Ubuntu (or other Debian-based Linux)".

All subsequent steps are for Ubuntu platforms:

- Install the prerequisite packages listed here: <https://heasarc.gsfc.nasa.gov/lheasoft/ubuntu.html>
- Build the software following the instructions in the installation guide (<https://heasarc.gsfc.nasa.gov/lheasoft/ubuntu.html>)
- Add the following lines to your `.bashrc` (or equivalent):

    ```sh
    export HEADAS=~/heasoft-6.28/x86_64-pc-linux-gnu-libc2.23
    . $HEADAS/headas-init.sh
    ```

### Install the calibration tree

1. Create a new folder “caldb” in the heasoft-6.28 folder
2. Follow the instructions on: <https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/install.html> (Sections 2 and 3)

### Install wcstools

1. Download the current version (3.9.6) from <http://tdc-www.harvard.edu/software/wcstools/wcstools-3.9.6.tar.gz>
2. Put the tarfile in your home folder and untar
3. Install the tools:

    ```sh
    cd wcstools-3.9.6
    make all
    ```

4. Add the following line to your `.bashrc` (or equivalent):

    ```sh
    export PATH=~/wcstools-3.9.6/bin:$PATH
    ```

More info can be found on the wcstools <a href="http://tdc-www.harvard.edu/wcstools/" target="_blank">website</a>.

### Install DRESSCode

Requires Python >= 3.7. Make sure you have a working python environment then install from source:

```cmd
pip install https://git+https://github.com/spacetelescope/DRESSCode.git
```

Alternatively, clone the repo to a directory install from there:

1. `git clone git@github.com:spacetelescope/DRESSCode.git`
2. `cd DRESSCode`
3. `pip install .` or for an editable install `pip install -e .`

To install extra dev dependencies: `pip install -e ".[dev]"`
