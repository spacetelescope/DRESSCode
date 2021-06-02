# Installation Instructions

## Download the software

- Go to <https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/download.html>
- STEP 1
    - Select the type of software: Choose "SOURCE CODE DISTRIBUTION"
    - Choose your platform, e.g. "PC - Ubuntu Linux 20.04"
- STEP 2
    - Download the desired packages: Select the "Swift" mission (all FTOOLS and XANADU will automatically be selected)
- Submit and wait
- Untar the file

## Install/Build the software

- STEP 3 - Install the software: Follow the installation guide for your platform, e.g. "PC Linux - Ubuntu (or other Debian-based Linux)".

All subsequent steps are for Ubuntu platforms:

- Install the prerequisite packages listed here: <https://heasarc.gsfc.nasa.gov/lheasoft/ubuntu.html>
- Build the software following the instructions in the installation guide (<https://heasarc.gsfc.nasa.gov/lheasoft/ubuntu.html>)
- Add the following lines to your `.bashrc` (or equivalent):

    ```sh
    export HEADAS=~/heasoft-6.25/x86_64-pc-linux-gnu-libc2.23
    . $HEADAS/headas-init.sh
    ```

## Install the calibration tree

1. Create a new folder “caldb” in the heasoft-6.25 folder
2. Follow the instructions on: <https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/install.html> (Sections 2 and 3)

## Install wcstools

1. Go to: <http://tdc-www.harvard.edu/wcstools/>
2. Choose the full package via HTTP from <http://tdc-www.harvard.edu/software/wcstools/wcstools-3.9.6.tar.gz>
3. Put the tarfile in your home folder and untar
4. Install the tools:

    ```sh
    cd wcstools-3.9.6
    make all
    ```

5. Add the following line to your `.bashrc` (or equivalent):

    ```sh
    export PATH=~/wcstools-3.9.5/bin:$PATH
    ```

## Download the DRESSCode from GitHub

- Python is needed to run the scripts. The DRESSCode was written and tested in python 3.6.8. Make sure you have a working python environment, preferably using Anaconda (or Astroconda).
