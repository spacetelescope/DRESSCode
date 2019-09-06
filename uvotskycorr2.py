#uvotskycorr2.py: Script to calculate and apply the aspect correction, using the updated attitude file.
#Created on 16-01-2019.
#Marjorie Decleir
#Note: This script requires the WCSTools. Make sure this is properly installed. Most of the time, errors occuring while running this script can be attributed to a problem with the WCSTools.

#Import the necessary packages.
import os
import shutil
import subprocess
import configloader


#Load the configuration file.
config = configloader.load_config()

#Specify the galaxy and the path to the working directory.
galaxy = config['galaxy']
path = config['path']  + galaxy + "/working_dir/"


#Print user information.
print("Calculating and applying aspect corrections...")

#Initialize the counter and count the total number of sky images. Initialize the error flag.
i = 0
num = sum(1 for filename in sorted(os.listdir(path)) if filename.endswith("sk.img") and "uat" in filename)
error = False

#For all files in the working directory:
for original_filename in sorted(os.listdir(path)):
    
    #If the file is not a sky image (created with the uat attitude file), skip this file and continue with the next file.
    if not original_filename.endswith("sk.img") or not "uat" in original_filename: continue
    
    #Copy the original file and give the copy another name. This copy will be the file to work with.
    filename = original_filename.replace("sk", "sk_corr")
    shutil.copyfile(path+original_filename, path+filename)

    #Specify the input skyfile, the output file, the attitude file, the terminal output file and the path to the catalog file.
    skyfile = filename
    outfile = original_filename.replace("sk.img", "aspcorr.ALL")
    attfile = original_filename.split('_',1)[0] + "uat.fits"
    terminal_output_file = path + "output_uvotskycorrID_" + original_filename.replace('.img','.txt')
    catfile = "/home/mdcleir/Documents/SWIFT_datareduction_pipeline/V2/usnob1.spec"

    #Open the terminal output file and run uvotskycorr ID with the specified parameters:
    with open(terminal_output_file,"w") as terminal:
        subprocess.call("uvotskycorr what=ID skyfile=" + skyfile + " corrfile=NONE attfile=" + attfile + " outfile=" + outfile + " starid='matchtol=20 cntcorr=3 n.reference=200 n.observation=40 max.rate=1000' catspec=" + catfile + " chatter=5", cwd=path, shell=True, stdout=terminal)

    #Check if an aspect correction was found.
    file = open(terminal_output_file,"r")

    for line in file:
        #If the words "no correction" are encountered, print an error message.
        if "no correction" in line:
            print("!! No aspect correction found for frame " + line.split()[4].replace("sk_corr","sk") + "!!")
            error = True

    #Print user information.
    i += 1
    print("Aspect correction calculated for all (other) frames of " + original_filename + " (" + str(i) + "/" + str(num) + ")")

    #Specify the correction file and the terminal output file.
    corrfile = original_filename.replace("sk.img","aspcorr.ALL")
    terminal_output_file = path+"output_uvotskycorrSKY_" + original_filename.replace('.img','.txt')

    #Open the terminal output file and run uvotskycorr SKY with the specified parameters:
    with open(terminal_output_file,"w") as terminal:
        subprocess.call("uvotskycorr what=SKY skyfile=" + skyfile + " corrfile=" + corrfile + " attfile=" + attfile + " outfile=NONE catspec=" + catfile, cwd=path, shell=True, stdout=terminal)

    #Check if the aspect correction was applied.
    file = open(terminal_output_file,"r")
    text = file.read()
        
    #If the word "error" is encountered, print an error message.
    if "error" in text:
        print("An error has occured during the application of the aspect correction to image " + original_filename)
        error = True

	#Print user information.
    print("Aspect correction applied to all (other) frames of " + original_filename + " (" + str(i) + "/" + str(num) + ")")

	#Do the same for the corresponding exposure map.
    or_expname = original_filename.replace("sk","ex")
    expname = or_expname.replace("ex", "ex_corr")
    shutil.copyfile(path+or_expname, path+expname)
    skyfile = expname
    terminal_output_file = path+"output_uvotskycorrSKY_" + or_expname.replace('.img','.txt')

    with open(terminal_output_file,"w") as terminal:
        subprocess.call("uvotskycorr what=SKY skyfile=" + skyfile + " corrfile=" + corrfile + " attfile=" + attfile + " outfile=NONE catspec=" + catfile, cwd=path, shell=True, stdout=terminal)

    file = open(terminal_output_file,"r")
    text = file.read()
        
    #If the word "error" is encountered, print an error message.
    if "error" in text:
        print("An error has occured during the application of the aspect correction to exposure map " + or_expname)
        error = True

	#Print user information.
    print("Aspect correction applied to all (other) frames of " + or_expname + " (" + str(i) + "/" + str(num) + ")")

    #Do the same for the corresponding mask file.
    or_maskname = original_filename.replace("sk","mk")
    maskname = or_maskname.replace("mk", "mk_corr")
    shutil.copyfile(path+or_maskname, path+maskname)
    skyfile = maskname
    terminal_output_file = path+"output_uvotskycorrSKY_" + or_maskname.replace('.img','.txt')

    with open(terminal_output_file,"w") as terminal:
        subprocess.call("uvotskycorr what=SKY skyfile=" + skyfile + " corrfile=" + corrfile + " attfile=" + attfile + " outfile=NONE catspec=" + catfile, cwd=path, shell=True, stdout=terminal)

    file = open(terminal_output_file,"r")
    text = file.read()
        
    #If the word "error" is encountered, print an error message.
    if "error" in text:
        print("An error has occured during the application of the aspect correction to maskf file " + or_maskname)
        error = True

	#Print user information.
    print("Aspect correction applied to all (other) frames of " + or_maskname + " (" + str(i) + "/" + str(num) + ")")


#Print user information.
if error == False:
    print("Aspect corrections were successfully calculated and applied to all frames in all sky images, exposure maps and mask files.")


