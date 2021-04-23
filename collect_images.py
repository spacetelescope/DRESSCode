#collect_images.py: Script to collect all raw files needed in the data reduction.
#Marjorie Decleir
#Created on 24-10-2018.
#Updated on 10-01-2019 (to add the uaf.hk files).

#Import the necessary packages.
import os
import shutil
import configloader


#Load the configuration file.
config = configloader.load_config()

#Specify the galaxy and the path to the working directory.
galaxy = config['galaxy']
path = config['path']  + galaxy

#Define the paths of the raw data and of the new directory with raw images.
rawpath = path + "/Raw_data/"
topath = path + "/Raw_images/"


#Create a new directory with all the raw UV images (*_rw.img.gz) from the uvot/image/ folders, the UV event files (*w1po_uf.evt.gz) from the uvot/event/ folders, the attitude (*pat.fits.gz) files from the auxil/ folders and the aspect following (*uaf.hk.gz) files from the uvot/hk/ folders.
#Initialize the counters.
i=0
j=0
k=0
l=0

#Create the new directory.
os.mkdir(topath)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

#For each subfolder in the Raw_data folder:
for directory in listdir_nohidden(rawpath):
	#Collect the raw UV images.
    for file in listdir_nohidden(rawpath+directory+"/uvot/image/"):
        if file.endswith("m2_rw.img.gz") or file.endswith("w1_rw.img.gz") or file.endswith("w2_rw.img.gz"):
            shutil.copy(rawpath+directory+"/uvot/image/"+file,topath)
            i += 1
	
	#Collect the UV event files.
    if os.path.isdir(rawpath+directory+"/uvot/event/"):
        for file in listdir_nohidden(rawpath+directory+"/uvot/event/"):
            if file.endswith("m2w1po_uf.evt.gz") or file.endswith("w1w1po_uf.evt.gz") or file.endswith("w2w1po_uf.evt.gz"):
                shutil.copy(rawpath+directory+"/uvot/event/"+file,topath)
                j += 1

	#Collect the attitude files.
    for file in listdir_nohidden(rawpath+directory+"/auxil/"):
        if file.endswith("pat.fits.gz"):
            shutil.copy(rawpath+directory+"/auxil/"+file,topath)
            k += 1

	#Collect the aspect following files.
    for file in listdir_nohidden(rawpath+directory+"/uvot/hk/"):
        if file.endswith("uaf.hk.gz"):
            shutil.copy(rawpath+directory+"/uvot/hk/"+file,topath)
            l += 1

#Print user information.
print(str(i) + " raw image files, " + str(j) + " event files, " + str(k) + " attitude files and " + str(l) + " aspect following files have been copied to " + topath)


