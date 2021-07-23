"""scan background image processing logs for aspect correction errors"""

import csv
from datetime import datetime
from pathlib import Path

from astropy.io import fits
from pyquaternion import Quaternion
from tqdm import tqdm

background_image_dir = Path("/astro/dust_kg3/bfalk/background_test_aspect_corr/")
count_files = 0
count_frames = 0
count_errors = 0

timestamp = datetime.now().isoformat()


def check_log(skycorr_log, update_global_counts=True):
    """check/count errors in the skycorr log"""
    global count_files
    global count_errors

    with open(skycorr_log) as skycorr_log_fh:
        if update_global_counts:
            count_files += 1
        frame_errors = 0
        corrections = []
        for line_no, line in enumerate(skycorr_log_fh):
            if "no correction" in line:
                # print(f'File "{skycorr_log}", line {line_no+1}\n  {line}')
                if update_global_counts:
                    count_errors += 1
                frame_errors += 1
                continue

            if "aspcorr: solution: quaternion" in line:
                # parse the string to float
                quaternion_str = line.split("aspcorr: solution: quaternion ")[1].strip()

                quaternion = Quaternion(
                    list(
                        map(
                            float,
                            quaternion_str.split(" "),
                        )
                    )
                )
                corrections.append(quaternion.degrees)

    return frame_errors, corrections


with open(
    f"background_images/aspect_correction_results_{timestamp}.csv", "w", newline=""
) as csvfile:
    fieldnames = [
        "obs",
        "filter",
        "frames_first_pass",
        "errors_first_pass",
        "first_pass_corr",
        "second_pass",
        "second_pass_errors",
        "second_pass_corr",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for obsid_dir in tqdm(sorted(background_image_dir.iterdir())):

        skycorr_logs = Path(obsid_dir / "working_dir").glob(
            "output_uvotskycorrID_*.txt"
        )
        skycorr_logs_second_pass = sorted(
            Path(obsid_dir / "working_dir").glob("output_uvotskycorrID_*_uat_*.txt")
        )
        skycorr_logs_first_pass = sorted(
            list(set(skycorr_logs) - set(skycorr_logs_second_pass))
        )

        if len(skycorr_logs_first_pass) == 0:
            writer.writerow({"obs": obsid_dir.name, "frames_first_pass": 0})
            continue

        # for each filter in the first pass...
        for skycorr_log in skycorr_logs_first_pass:
            frame_errors, first_pass_corr = check_log(skycorr_log)

            # check errors in the second pass log
            # get second pass log from first pass log name
            second_pass_log = second_pass_log = Path(
                skycorr_log.parent,
                "".join([skycorr_log.name[:-15], "_uat", skycorr_log.name[-15:]]),
            )

            second_pass_frame_errors = None
            second_pass_corr = None
            if second_pass_log.exists():
                second_pass_frame_errors, second_pass_corr = check_log(
                    second_pass_log, update_global_counts=False
                )

            # count the frames in the img file
            raw_image_file = skycorr_log.name.replace(
                "output_uvotskycorrID_", ""
            ).replace("sk.txt", "rw.img")
            with fits.open(
                skycorr_log.parent / raw_image_file, lazy_load_hdus=False
            ) as hdulist:
                # first is a top level header (HDU: header data unit)
                frames = len(hdulist) - 1

            count_frames += frames

            writer.writerow(
                {
                    "obs": obsid_dir.name,
                    "filter": skycorr_log.name[-10:-7],
                    "frames_first_pass": frames,
                    "errors_first_pass": frame_errors,
                    "first_pass_corr": first_pass_corr,
                    "second_pass": second_pass_log.exists(),
                    "second_pass_errors": second_pass_frame_errors,
                    "second_pass_corr": second_pass_corr,
                }
            )

print("total filters processed", count_files)
print("total frames processed", count_frames)
print("frame errors", count_errors)
