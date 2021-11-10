"""
collect_images.py: Script to collect all raw files needed in the data reduction.
"""

# Import the necessary packages.
import os
import shutil

import configloader
from utils import listdir_nohidden

# Load the configuration file.
config = configloader.load_config()

# Specify the galaxy and the path to the working directory.
galaxy = config["galaxy"]
path = config["path"] + galaxy

# Define the paths of the raw data and of the new directory with raw images.
rawpath = path + "/Raw_data/"
topath = path + "/Raw_images/"


# Create a new directory with all the raw UV images (*_rw.img.gz) from the uvot/image/
# folders, the UV event files (*w1po_uf.evt.gz) from the uvot/event/ folders, the
# attitude (*pat.fits.gz) files from the auxil/ folders and the aspect following
# (*uaf.hk.gz) files from the uvot/hk/ folders.
# Initialize the counters.
raw_image_file_count = 0
event_file_count = 0
attitude_file_count = 0
aspect_file_count = 0

# Create the new directory.
os.mkdir(topath)

# For each subfolder in the Raw_data folder:
for directory in listdir_nohidden(rawpath):
    # Collect the raw UV images.
    for file in listdir_nohidden(rawpath + directory + "/uvot/image/"):
        if (
            file.endswith("m2_rw.img.gz")
            or file.endswith("w1_rw.img.gz")
            or file.endswith("w2_rw.img.gz")
        ):
            shutil.copy(rawpath + directory + "/uvot/image/" + file, topath)
            raw_image_file_count += 1

    # Collect the UV event files.
    if os.path.isdir(rawpath + directory + "/uvot/event/"):
        for file in listdir_nohidden(rawpath + directory + "/uvot/event/"):
            if (
                file.endswith("m2w1po_uf.evt.gz")
                or file.endswith("w1w1po_uf.evt.gz")
                or file.endswith("w2w1po_uf.evt.gz")
            ):
                shutil.copy(rawpath + directory + "/uvot/event/" + file, topath)
                event_file_count += 1

    # Collect the attitude files.
    for file in listdir_nohidden(rawpath + directory + "/auxil/"):
        if file.endswith("pat.fits.gz"):
            shutil.copy(rawpath + directory + "/auxil/" + file, topath)
            attitude_file_count += 1

    # Collect the aspect following files.
    for file in listdir_nohidden(rawpath + directory + "/uvot/hk/"):
        if file.endswith("uaf.hk.gz"):
            shutil.copy(rawpath + directory + "/uvot/hk/" + file, topath)
            aspect_file_count += 1

# Print user information.
print(
    str(raw_image_file_count)
    + " raw image files, "
    + str(event_file_count)
    + " event files, "
    + str(attitude_file_count)
    + " attitude files and "
    + str(aspect_file_count)
    + " aspect following files have been copied to "
    + topath
)
