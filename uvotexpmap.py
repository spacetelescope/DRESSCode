#uvotexpmap2.py: Script to create exposure maps, using the updated attitude file.
#Created on 09-12-2015, updated (to Python 3.6) on 26-10-2018.
#Updated on 10-01-2019 (based on feedback Bob).
#Updated on 15-04-2019 (to include the sss masks).
#Marjorie Decleir

#Import the necessary packages.
import os
import subprocess
from astropy.io import fits
import numpy as np
import configloader


#Load the configuration file.
config = configloader.load_config()

#Specify the galaxy and the path to the working directory.
galaxy = config['galaxy']
path = config['path']  + galaxy + "/working_dir/"


#Print user information.
print("Creating exposure maps...")

#Initialize the counter and count the total number of sky images. Initialize the error flag.
i = 0
num = sum(1 for filename in sorted(os.listdir(path)) if filename.endswith("sk.img") and "uat" in filename)
error = False

#Open the sss masks.
sss_1x1 = np.ma.make_mask(fits.open("sss/sss_UV_1x1.fits")[0].data)
sss_2x2 = np.ma.make_mask(fits.open("sss/sss_UV_2x2.fits")[0].data)

#For all files in the working directory:
for filename in sorted(os.listdir(path)):
    
    #If the file is not a sky image (created with the uat attitude file), skip this file and continue with the next file.
    if not filename.endswith("sk.img") or not "uat" in filename: continue

    #Open the bad pixel file and copy its primary header (extension 0 of hdulist) to a new hdulist.
    badpixfile = "quality_" + filename.replace("sk","badpix")
    badpix_hdulist = fits.open(path+badpixfile)
    new_badpix_header = fits.PrimaryHDU(header=badpix_hdulist[0].header)
    new_badpix_hdulist = fits.HDUList([new_badpix_header])

    #For all frames in the bad pixel file: Update the bad pixel mask to include the sss mask.
    for j in range(1,len(badpix_hdulist)):
        new_data = badpix_hdulist[j].data
        if new_data.shape == (1024,1024):
            new_data[~sss_2x2] = 5.
        elif new_data.shape == (2048,2048):
            new_data[~sss_1x1] = 5.
        else:
            print("Quality map " + badpixfile + "[" + str(j) + "] does not have the correct dimensions, and cannot be combined with an sss mask.")
            error = True
        new_badpix_hdu = fits.ImageHDU(new_data,badpix_hdulist[j].header)
        new_badpix_hdulist.append(new_badpix_hdu)

    #Write out the updated bad pixel file.
    new_badpix_hdulist.writeto(path+badpixfile.replace(".img","_new.img"),overwrite=True)
    
    #Specify the input file, the output file, the bad pixel file, the attitude file, the output mask file and the terminal output file.
    infile = filename
    outfile = filename.replace("sk","ex")
    badpixfile = badpixfile.replace(".img","_new.img")
    attfile = filename.split('_',1)[0] + "uat.fits"
    maskfile = filename.replace("sk","mk")
    trackfile = filename.split('_',1)[0] + "uaf.hk"
    terminal_output_file = path + "output_uvotexpmap_" + filename.replace('.img','.txt')

    #Open the terminal output file and run uvotexpmap with the specified parameters:
    with open(terminal_output_file,"w") as terminal:
        subprocess.call("uvotexpmap infile=" + infile + " badpixfile=" + badpixfile + " method=SHIFTADD attfile=" + attfile + " teldeffile=CALDB outfile=" + outfile + " maskfile=" + maskfile + " masktrim=8 trackfile=" + trackfile + " attdelta=0.1 refattopt='ANGLE_d=5,OFFSET_s=1000'", cwd=path, shell=True, stdout=terminal)

    #Check if the exposure map was successfully created.
    file = open(terminal_output_file,"r")
    text = file.read()
    
    #If the word "error" is encountered or if the words "all checksums are valid" are not encountered, print an error message.
    if "error" in text or not "created output image" in text:
        print("An error has occured for image " + filename)
        error = True

    #Print user information.
    i += 1
    print("Exposure map created for all (other) frames of " + filename + " (" + str(i) + "/" + str(num) + ")")
    
#Print user information.
if error == False:
    print("Exposure maps were successfully created for all sky images.")


