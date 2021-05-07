#uvotskycorr.py: Script to calculate the aspect correction.
#Created on 08-12-2015, updated (to Python 3.6) on 25-10-2018.
#Marjorie Decleir
#Note: This script requires the WCSTools. Make sure this is properly installed. Most of the time, errors occuring while running this script can be attributed to a problem with the WCSTools.
#Updated on 11-01-2019 (based on feedback Bob).

#Import the necessary packages.
import os
import subprocess
import configloader


#Load the configuration file.
config = configloader.load_config()

#Specify the galaxy and the path to the working directory.
galaxy = config['galaxy']
path = config['path']  + galaxy + "/working_dir/"


#Print user information.
print("Calculating aspect corrections...")

#Initialize the counter and count the total number of sky images. Initialize the error flag.
i = 0
num = sum(1 for filename in sorted(os.listdir(path)) if filename.endswith("sk.img"))
error = False

#For all files in the working directory:
for filename in sorted(os.listdir(path)):
    
    #If the file is not a sky image, skip this file and continue with the next file.
    if not filename.endswith("sk.img"): continue
    
    #Specify the input skyfile, the output file, the attitude file, the terminal output file and the path to the catalog file.
    skyfile = filename
    outfile = filename.replace("sk.img", "aspcorr.ALL")
    attfile = filename.split('_',1)[0] + "pat.fits"
    terminal_output_file = path + "output_uvotskycorrID_" + filename.replace('.img','.txt')
    catfile = os.getcwd() + "/usnob1.spec"

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
    print("Aspect correction calculated for all (other) frames of " + filename + " (" + str(i) + "/" + str(num) + ")")


#Print user information.
if error == False:
    print("Aspect corrections were successfully calculated for all frames in all sky images.")


