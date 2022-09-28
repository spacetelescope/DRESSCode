# Using DRESSCode

*Note*: The details of the different steps in the pipeline are explained in Chapter 2 of <a href="https://biblio.ugent.be/publication/8638711" target="_blank">Marjorie Decleir's PhD thesis</a>.

Before running these steps, make sure you have [installed the software](install.md) and [downloaded and prepared the data](download_data.md).

## Run the entire pipeline

To run the entire pipeline, you can run this script: [`pipeline.bash`](https://github.com/spacetelescope/DRESSCode/blob/main/pipeline.bash){:target="_blank"}. To run the pipeline step-by-step, see instructions below.

## Step by step

### Sky images part 1

Run the script `dc-uvotimage` to create sky images from the raw images and event files. When your data contains event files, you will get the following warning:

`uvotimage: skipping event based image HDU w1386106344E in file sw00032766001uw1_rw.img`

This means that the code is skipping the event based frames in the raw images to prevent using the event data twice. This is perfectly normal, and you can thus ignore this warning.

### Aspect correction part 1

- Run the script `dc-uvotskycorr` to calculate an aspect correction for the sky images.
If no aspect correction could be found, the following warning will appear:

    `!! No aspect correction found for frame sw00450884000_evt_uw2_sk.img[1]!!`

    To solve this, you can try to increase the number of reference stars used by the task. In the script you will find: `n.reference=200 n.observation=40`. `n.reference` is the maximum number of reference stars that will be used from the catalog. `n.observation` is the maximum number of observed stars in the image that will be used to match with the catalog. Increasing one (or both) of these values can help to find an aspect correction. Of course, this will also increase the running time. Too high values can cause the process to crash, for example when your computer is short of memory. Frames for which no aspect correction was found, will not be taken into account in the summed image (see [Summing images per observing period](#summing-images-per-observing-period)).

- Run the script `dc-uvotattcorr` to adjust the attitude files with the calculated aspect corrections.

### Sky images part 2

Run the script `dc-uvotimage2` to create new sky images from the raw images, using the updated attitude files.

### Auxiliary files part 1

- Run the script `dc-uvotbadpix` to create quality maps for all sky images.
- Run the script `dc-uvotexpmap` to create exposure maps for all sky images, to flag the sss patches in the quality maps, and to create mask maps based on the quality maps.

Small scale sensitivity (sss) patches are detector regions with a lower throughput, probably caused by dust on the photocathode. There is no way to correct for the count loss in the affected pixels. Therefore, the only solution is to mask these regions in the images. The script `dc-uvotexpmap` will flag these pixels in the quality maps. At this stage, only raw image files of 1024x1024 or 2048x2048 pixels can be used. Some galaxies have images with a different dimension. For these images, an sss mask cannot be created, because it is a priori not known which part of the detector was exposed. These images should thus not be used in the pipeline. When the script encounters an image with a different dimension, the following warning will appear:

`Quality map quality_sw00032081026_uat_img_uw1_badpix.img[1] does not have the correct dimensions, and cannot be combined with an sss mask.`

Make sure to delete these images before continuing!

### Aspect correction part 2

Run the script `dc-uvotskycorr2` to calculate an aspect correction and apply it to the sky images, the exposure maps and the mask files, using the updated attitude files.

### Auxiliary files part 2

Run the script `dc-uvotskylss` to create large scale sensitivity (lss) maps for all sky images.

### Flux corrections

Run the script `dc-corrections` to correct the normalized images for coincidence loss, large scale sensitivity variations, and loss of detector sensitivity (i.e. zero point correction).

### Summing images

- Run the script `dc-uvotimsum` to sum all frames per type and per filter and to normalize the total sky images. Image frames for which no aspect correction was found, will automatically be excluded from the sum.

### Calibration and aperture correction

Use the script `dc-calibration` to convert the units of the final images from counts/s to Jy and to perform an “inverse” aperture correction.
