DRESSCode
=========

DRESSCode, short for Data Reduction of Extended Swift Sources Code, is a fully automated pipeline to reduce Swift UVOT images of extended sources. It consists of a series of python scripts that perform the different steps of the data reduction pipeline to all images. The different steps include preparation, creation of sky images, aspect correction, creation of auxiliary maps, combination of separate frames, several corrections to the flux, combination of different observing periods, calibration, and aperture correction. DRESSCode is a two-phase pipeline, which means that some steps are repeated a second time, in order to improve the accuracy of the astrometry of the images.


Documentation
-------------

- Please refer to `DRESSCode_UserManual.pdf` for detailed installation instructions and a user manual.

- The details of the different steps in the pipeline are explained in Chapter 2 of `Marjorie Decleir's PhD thesis <https://biblio.ugent.be/publication/8638711>`_.

In order to execute the full pipeline exactly as described in the manual, it is recommended to keep the same directory structure as explained in the manual. The user then only needs to change the galaxy name and the path of the main directory in the configuration file `config.txt` before running the scripts.


Requirements
------------

DRESSCode has been written and tested on Linux (Ubuntu 16.04), using python 3.6.8, and relies on several tasks from the specialized HEASoft software, provided by NASA.

The minimum requirements are thus:

- Python 3.6 or later

- HEASoft 6.25 or later, which can be downloaded from the `HEASARC website <https://heasarc.gsfc.nasa.gov/docs/software/heasoft/download.html>`_. The installation guide and user manual `DRESSCode_UserManual.pdf` explains the HEASoft installation step by step. Note that DRESSCode has been written and tested for HEASoft version 6.25. A later version should work as well, but possibly some minor changes are needed to the scripts.


Contributors
------------

Marjorie Decleir


License
-------

This project is Copyright (c) Marjorie Decleir and licensed under
the terms of the BSD 3-Clause “New” or “Revised” License (see the `LICENSE.txt` file for more information).


Publications
------------

A slightly older version of the pipeline (with only one phase) has been used and described in `Decleir et al. (2019) <https://ui.adsabs.harvard.edu/abs/2019MNRAS.486..743D/abstract>`_.
