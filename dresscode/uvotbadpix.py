"""
uvotbadpix.py: Script to create quality maps.
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
print("Creating quality maps...")

# Initialize the counter and count the total number of sky images.
i = 0
num = sum(
    1
    for filename in sorted(os.listdir(path))
    if filename.endswith("sk.img") and "uat" in filename
)
# Initialize the error flag.
error = False

# For all files in the working directory:
for filename in sorted(os.listdir(path)):

    # If the file is not a sky image (created with the uat attitude file), skip this
    # file & continue with the next file.
    if not filename.endswith("sk.img") or "uat" not in filename:
        continue

    # Specify the input file, the output file and the terminal output file.
    infile = filename
    outfile = "quality_" + filename.replace("sk", "badpix")
    terminal_output_file = (
        path + "output_uvotbadpix_" + filename.replace(".img", ".txt")
    )

    # Open the terminal output file and run uvotbadpix with the specified parameters:
    with open(terminal_output_file, "w") as terminal:
        subprocess.call(
            "uvotbadpix infile=" + infile + " badpixlist=CALDB outfile=" + outfile,
            cwd=path,
            shell=True,
            stdout=terminal,
        )

    # Check if the badpixel file was succesfully created.
    file = open(terminal_output_file, "r")
    text = file.read()

    # If the word "error" is encountered or if the words "created output image" are not
    # encountered, print an error message.
    if "error" in text or "created output image" not in text:
        print("An error has occurred for image " + filename)
        error = True

    # Print user information.
    i += 1
    print(
        "Quality map created for all (other) frames of "
        + filename
        + " ("
        + str(i)
        + "/"
        + str(num)
        + ")"
    )

# Print user information.
if error is False:
    print("Quality maps were successfully created for all sky images.")
