import os


def listdir_nohidden(path):
    """generator that yields filepaths that aren't hidden (start with a `.`)"""
    for f in os.listdir(path):
        if not f.startswith("."):
            yield f


def load_config(config_file):
    """Function to open and read the configuration file"""
    config = {}
    with open(config_file, "r") as configfile:
        for line in configfile:
            splitline = line.split("=")
            key, value = splitline[0].strip(), splitline[1].strip()
            if key == "years":
                if ", " in value:
                    value = [y.strip() for y in value.split(",")]
                else:
                    value = [value]
            config[key] = value
    return config
