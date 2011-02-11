import os
from shutil import rmtree

def count_files(folder):
    """Recursively counts files in a folder. Does not count folders."""
    r = 0
    l = os.listdir(folder)
    if not l:
        return r
    for f in l:
        if os.path.isdir(os.path.join(folder, f)):
            r += count_files(os.path.join(folder, f))
        else:
            r += 1
    return r


def recursive_cleaner(folder):
    """Recursively check folders and removes if it's empty"""
    l = os.listdir(folder)
    for f in l:
        addr = os.path.join(folder, f)
        if os.path.isdir(addr) and not count_files(addr):
            rmtree(os.path.join(folder, f))


if __name__ == "__main__":
    recursive_cleaner("/home/osa1/Desktop/testler")
