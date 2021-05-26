# DRESSCode

DRESSCode, short for Data Reduction of Extended Swift Sources Code, is a fully automated pipeline to reduce Swift UVOT images of extended sources. It consists of a series of python scripts that perform the different steps of the data reduction pipeline to all images. The different steps include preparation, creation of sky images, aspect correction, creation of auxiliary maps, combination of separate frames, several corrections to the flux, combination of different observing periods, calibration, and aperture correction. DRESSCode is a two-phase pipeline, which means that some steps are repeated a second time, in order to improve the accuracy of the astrometry of the images.

For the original version of this software, see [mdecleir/DRESSCode](https://github.com/mdecleir/DRESSCode).

## Documentation

- Please refer to [DRESSCode_UserManual.pdf](DRESSCode_UserManual.pdf) for detailed installation instructions and a user manual.
- The details of the different steps in the pipeline are explained in Chapter 2 of [Marjorie Decleir's PhD thesis](https://biblio.ugent.be/publication/8638711).

In order to execute the full pipeline exactly as described in the manual, it is recommended to keep the same directory structure as explained in the manual. The user then only needs to change the galaxy name and the path of the main directory in the configuration file `config.txt` before running the scripts.

## Requirements

DRESSCode has been written and tested on Linux and Mac, and relies on several tasks from the specialized [HEASoft](https://heasarc.gsfc.nasa.gov/docs/software/heasoft/) software, provided by NASA.

The minimum requirements are thus:

- Python 3.6 or later
- HEASoft 6.25 or later, which can be downloaded from the [HEASARC website](https://heasarc.gsfc.nasa.gov/docs/software/heasoft/download.html). The installation guide and user manual explain the HEASoft installation step by step. Note that DRESSCode has been written and tested for HEASoft version 6.25. A later version should work as well, but possibly some minor changes are needed to the scripts.

## License

This project is Copyright Association of Universities for Research in Astronomy and licensed under the terms of the BSD 3-Clause “New” or “Revised” License (see the [LICENSE.txt](LICENSE.txt) file for more information).

## Use cases and publications

- [Decleir et al. (2019)](https://ui.adsabs.harvard.edu/abs/2019MNRAS.486..743D/abstract) used a slightly older version of the DRESSCode (with only one phase) to reduce the Swift UVOT images of NGC628. These images were used to measure dust attenuation curves on resolved scales in NGC628. The paper also describes the details of the older version of the pipeline.
- The current version of the DRESSCode was used in the DustKING project, to reduce the Swift UVOT images of all KINGFISH galaxies. The goal of this project is to measure the global dust attenuation curves of all KINGFISH galaxies. This work will be published soon (Decleir et al., in prep.). The preliminary results of this work can be found in Chapter 4 of [Marjorie Decleir's PhD thesis](https://biblio.ugent.be/publication/8638711).
