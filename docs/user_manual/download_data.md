# Download and prepare the SWIFT data

## Download the data

- Go to NASA’s HEASARC Archive: <https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/swift.pl>
- Next to “UVOT Log”, click on “parameter search form” to open the SWIFT UVOT Data Query form.
- Use the following parameters (and leave the other parameters to the default values):

    |<!-- -->  | <!-- -->                              |
    | ------------  | -------------                    |
    | filter        | `UVW2` OR `UVM2` OR `UVW1`       |
    | pointing_mode | POINTING                         |
    | Object Name   | Name of the galaxy, e.g. NGC0628 |

- Click on the “Start Search” button and wait for the query results to load.
- Check the box “Select All” to select all data.
- At the bottom: Select “Swift Auxiliary Data (aux)” and “Swift UVOT Data (uvot data)”.
- Click on the “Create Download Script” button and wait for the new tab to load.
- Click on the “Download Commands To File” button and wait until the script is downloaded.
- Create a new directory somewhere on your computer with the name of the galaxy, e.g. “NGC0628”, and create a new directory within that directory with the name “Raw_data”.
- Move the download script to the “Raw_data” directory and run it:

    ```sh
    bash browse_download_script.txt
    ```

Downloading the data can take a while!

## Sort and select the required data

In order to execute the full pipeline, it is recommended to keep the same directory structure as explained here and in [data download](download_data.md). The user then only needs to change the galaxy name and the path of the main directory in the configuration file `config.txt` before running the scripts (see <a href="https://github.com/spacetelescope/DRESSCode/blob/main/config.txt.example" target="_blank">config.txt.example</a>).

- The download script will automatically sort the data into different directories according to the observing ID of the exposure. The directory structure is somewhat complex, but you should not worry about that. If you used the same directory structure as described above, the only thing you need to do to make all scripts work, is to change the name of the galaxy and the path of the main directory (in which the different galaxy directories are located) in the `config.txt` file.
- Run the script `collect_images.py` to collect all the UV raw image (`*_rw.img.gz`) files from the uvot/image/ folders, the UV event files (`*w1po_uf.evt.gz`) from the uvot/event/ folders, the attitude (`*pat.fits.gz`) files from the auxil/ folders and the aspect following (`*uaf.hk.gz`) files from the uvot/hk/ folders. This will create the directory “Raw_images” in the current directory (e.g. “NGC0628”).
- To save space on your computer, you can now delete the “Raw_data” directory, if you want.
- Extract (decompress) all files in the “Raw_images” directory. To save space on your computer, you can now delete the compressed (`*.gz`) files, if you want.
- Copy the entire “Raw_images” directory to a new working directory with the name “working_dir”, in which all the temporary files will be stored during the reduction process. Make sure you always keep the raw files in the “Raw_images” directory in case you want to restart.
