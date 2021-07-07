"""
uvotskylss.py: Script to create large scale sensitivity maps, using the updated
attitude file and after the aspect correction.
"""

# Import the necessary packages.
import os
import subprocess

import configloader

# Load the configuration file.
config = configloader.load_config()

# Specify the galaxy and the path to the working directory.
galaxy = config["galaxy"]
path = config["path"] + galaxy + "/working_dir/"


# Print user information.
print("Creating large scale sensitivity maps...")

# Initialize the counter and count the total number of corrected sky images. Initialize
# the error flag.
i = 0
num = sum(
    1 for filename in sorted(os.listdir(path)) if filename.endswith("sk_corr.img")
)
error = False

# For all files in the working directory:
for filename in sorted(os.listdir(path)):

    # If the file is not an aspect corrected sky image (created with the uat attitude
    # file), skip this file and continue with the next file.
    if not filename.endswith("sk_corr.img"):
        continue

    # Specify the input file, the output file, the attitude file and the terminal output
    # file.
    infile = filename
    outfile = filename.replace("sk", "lss")
    attfile = filename.split("_", 1)[0] + "uat.fits"
    terminal_output_file = (
        path + "output_uvotskylss_" + filename.replace(".img", ".txt")
    )

    # Open the terminal output file and run uvotskylss with the specified parameters:
    with open(terminal_output_file, "w") as terminal:
        subprocess.call(
            "uvotskylss infile="
            + infile
            + " outfile="
            + outfile
            + " attfile="
            + attfile,
            cwd=path,
            shell=True,
            stdout=terminal,
        )

    # Check if the lss map was successfully created.
    file = open(terminal_output_file, "r")
    text = file.read()

    # If the word "error" is encountered, print an error message.
    if "error" in text:
        print("An error has occurred for image " + filename)
        error = True

    # Print user information.
    i += 1
    print(
        "Large scale sensitivity map created for all (other) frames of "
        + filename
        + " ("
        + str(i)
        + "/"
        + str(num)
        + ")"
    )

# Print user information.
if error is False:
    print("Large scale sensitivity maps were successfully created for all sky images.")
