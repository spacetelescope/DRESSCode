# DRESSCode: Swift data reduction

![DRESSCode](img/logo.svg){ loading=lazy }

<p align="right" style="font-size: .7rem">
    <em>DRESSCode logo designed by <a href="https://github.com/JDWree" target="_blank">J. De Wree</a></em>
</p>

DRESSCode, short for Data Reduction of Extended Swift Sources Code, is a fully automated pipeline to reduce Swift UVOT images of extended sources. It consists of a series of python scripts that perform the different steps of the data reduction pipeline to all images. The different steps include preparation, creation of sky images, aspect correction, creation of auxiliary maps, combination of separate frames, several corrections to the flux, combination of different observing periods, calibration, and aperture correction. DRESSCode is a two-phase pipeline, which means that some steps are repeated a second time, in order to improve the accuracy of the astrometry of the images.

For the original version of this software, see <a href="https://github.com/mdecleir/DRESSCode" target="_blank">mdecleir/DRESSCode</a>.

---

**Documentation**: [https://spacetelescope.github.io/DRESSCode/](index.md)

**Source Code**: <a href="https://github.com/spacetelescope/DRESSCode/">https://github.com/spacetelescope/DRESSCode/</a>

---

## Requirements

DRESSCode has been written and tested on Linux and Mac, and relies on several tasks from the specialized <a href="https://heasarc.gsfc.nasa.gov/docs/software/heasoft/" target="_blank">HEASoft</a> software, provided by NASA.

See the [documentation](user_manual/install.md) for specific installation instructions.

The minimum requirements are:

- Python 3.7 or later
- Current version of HEASoft (tested with 6.28)
- <a href="https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/install.html" target="_blank">caldb</a>: calibration tree
- <a href="http://tdc-www.harvard.edu/wcstools/" target="_blank">wcstools</a>: World Coordinate System utilities

### Docker

Docker can be used to run the software without having to complete the heasoft/caldb/wcstools installation procedure yourself (or to run on windows). The image can be found on <a href="https://hub.docker.com/r/dresscodeswift/dresscode" target="_blank">docker hub</a>.

To download and open an interactive shell:

```sh
docker pull dresscodeswift/dresscode
docker run --rm -it dresscodeswift/dresscode /bin/bash
```

From there run the pipeline, which is located in `/opt/dresscode`

For more, see our [docker instructions](user_manual/install.md).

## Help

Please see the [documentation](index.md). If you encounter a bug or have questions, please report through GitHub <a href="https://github.com/spacetelescope/DRESSCode/issues" target="_blank">issues</a>.

## License

This project is Copyright Association of Universities for Research in Astronomy and licensed under the terms of the BSD 3-Clause “New” or “Revised” License (see the [LICENSE](LICENSE.md) file for more information).

## Use cases and publications

- <a href="https://ui.adsabs.harvard.edu/abs/2019MNRAS.486..743D/abstract" target="_blank">Decleir et al. (2019)</a> used a slightly older version of the DRESSCode (with only one phase) to reduce the Swift UVOT images of NGC628. These images were used to measure dust attenuation curves on resolved scales in NGC628. The paper also describes the details of the older version of the pipeline.
- The current version of the DRESSCode was used in the DustKING project, to reduce the Swift UVOT images of all KINGFISH galaxies. The goal of this project is to measure the global dust attenuation curves of all KINGFISH galaxies. This work will be published soon (Decleir et al., in prep.). The preliminary results of this work can be found in Chapter 4 of <a href="https://biblio.ugent.be/publication/8638711" target="_blank">Marjorie Decleir's PhD thesis</a>.

## Contributing

We use [`black`](https://github.com/psf/black) and [`isort`](https://github.com/pycqa/isort) for autoformatting and [`flake8`](https://github.com/PyCQA/flake8) for linting.

You are encouraged to add editor support (enable autoformat on save w/ black) and show linting errors with flake8. See the documentation for your editor to set up.

To manually run each of the tools:

black:

```sh
black . --check --diff
```

isort:

```sh
isort . --check --diff
```

flake8:

```sh
flake8 .
```

We also have pre-commit hooks. You can install them with `pre-commit install`
