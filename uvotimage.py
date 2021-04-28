""" Script to create sky images from raw images and event files. """

import subprocess
from multiprocessing import Pool
from pathlib import Path
from typing import List, Sequence

from tqdm import tqdm
from astropy.io import fits

import configloader


def get_filenames(extensions: Sequence[str]) -> List[Path]:
    """ Return filenames from the  working directory and the path to the working directory """

    config = configloader.load_config()
    galaxy = config["galaxy"]
    working_dir_path = Path(config["path"] + galaxy + "/working_dir/")

    paths = []
    for ext in extensions:
        paths += list(working_dir_path.glob(ext))

    # todo: add exclude patterns
    return paths


def process_files(filename: Path):
    """ process a full filepath """

    error = False

    # Specify the input file, the prefix for the output file, the attitude file and the terminal output file.
    prefix = filename.name.split("u")[0] + "_" + filename.name.split(".")[1] + "_"
    attfile = filename.parent / "{}pat.fits".format(filename.name.split("u", 1)[0])
    terminal_output_file = filename.parent / f"output_uvotimage_{filename.stem}.txt"

    # Open the file and take the RA, DEC and roll from the header.
    with fits.open(filename) as hdul:
        header = hdul[0].header
    ra = header["RA_PNT"]
    dec = header["DEC_PNT"]
    pa = header["PA_PNT"]

    # Open the terminal output file and run uvotimage with the specified parameters.
    # uvotimage help page: https://heasarc.gsfc.nasa.gov/lheasoft/ftools/headas/uvotimage.html
    with open(terminal_output_file, "w") as terminal:
        try:
            subprocess.run(
                (
                    "uvotimage"
                    f" infile={filename}"
                    f" prefix={prefix}"
                    f" attfile={attfile}"
                    " teldeffile=CALDB alignfile=CALDB"
                    f" ra={ra}"
                    f" dec={dec}"
                    f" roll={pa}"
                    " mod8corr=yes refattopt='ANGLE_d=5,OFFSET_s=1000'"
                ),
                cwd=filename.parent,
                shell=True,
                stdout=terminal,
                check=True,
            )
        except subprocess.CalledProcessError:
            error = True
            print(f"error on file: {filename.name}")

    return error


def validate_terminal_output(filenames: List[Path]):

    num_files = len(filenames)
    errors = []

    for index, filename in enumerate(filenames):

        error = False

        terminal_output_file = filename.parent / f"output_uvotimage_{filename.stem}.txt"

        if not terminal_output_file.exists():
            continue

        # todo: do validation outside this function, so print statements present in order
        # Check if the sky image was successfully created.
        with open(terminal_output_file, "r") as file:
            for line in file:
                # If the word "error" is encountered, print an error message.
                if "error" in line:
                    print("An error has occured for image " + filename.name)
                    error = True

                # If uvotimage skipped an event based image HDU, let the user know.
                if "skipping event based image HDU" in line:
                    print(line, " in file " + filename.name)

        # Print user information.
        print(
            f"Sky image created for all (other) frames of {filename.name} ({index})/{num_files})"
        )
        errors.append(error)

    return errors


def main():

    filenames = get_filenames(["*rw.img", "*.evt"])

    print("Creating sky images...")

    errors = []

    #! error: "can't stat user parameter file .../sec2time.par" when running in parallel

    with Pool() as p:
        for result in tqdm(p.imap(process_files, filenames), total=len(filenames)):
            errors.append(result)

    print("validating results")
    errors_validation = validate_terminal_output(filenames)

    # Print user information.
    if not any(errors) and not any(errors_validation):
        print(
            "Sky images were successfully created for all raw images and event files."
        )


if __name__ == "__main__":
    main()
