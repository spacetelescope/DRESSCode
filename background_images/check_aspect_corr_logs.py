"""scan background image processing logs for aspect correction errors"""

import csv
from pathlib import Path

from astropy.io import fits

background_image_dir = Path("/astro/dust_kg3/bfalk/background_test_aspect_corr/")
count_files = 0
count_frames = 0
count_errors = 0

with open(
    "background_images/aspect_correction_results.csv", "w", newline=""
) as csvfile:
    fieldnames = ["obs", "filter", "frames", "errors"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for obsid_dir in sorted(background_image_dir.iterdir()):

        skycorr_logs = sorted(
            Path(obsid_dir / "working_dir").glob("output_uvotskycorrID_*.txt")
        )

        if len(skycorr_logs) == 0:
            writer.writerow({"obs": obsid_dir.name, "frames": 0})

        # for each filter...
        for skycorr_log in skycorr_logs:
            with open(skycorr_log) as skycorr_log_fh:
                count_files += 1
                frame_errors = 0
                for line_no, line in enumerate(skycorr_log_fh):
                    if "no correction" in line:
                        # print(f'File "{skycorr_log}", line {line_no+1}\n  {line}')
                        count_errors += 1
                        frame_errors += 1

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
                    "frames": frames,
                    "errors": frame_errors,
                }
            )

print("total filters processed", count_files)
print("total frames processed", count_frames)
print("frame errors", count_errors)
