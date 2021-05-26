import os


def listdir_nohidden(path):
    """generator that yields filepaths that aren't hidden (start with a `.`)"""
    for f in os.listdir(path):
        if not f.startswith("."):
            yield f
