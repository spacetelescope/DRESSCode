# configloader.py: Script to load the configuration file (config.txt).
# Marjorie Decleir
# Created on 6-08-2019.

# Import the necessary package.
import os

# Define the path to the configuration file.
config_file = os.path.dirname(os.path.realpath(__file__)) + "/config.txt"

# Function to open and read the configuration file.
def load_config():
    config = {}
    with open(config_file, "r") as configfile:
        for line in configfile:
            splitline = line.split(" = ")
            key, value = splitline[0].strip(), splitline[1].strip()
            if key == "years":
                if ", " in value:
                    value = value.split(", ")
                else:
                    value = [value]
            config[key] = value
    return config
