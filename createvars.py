import os
import shelve


def createShelfFolder():
    # define the name of the directory to be created
    path = "../vars/"

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)
        try:
            path += "vars.txt"
            f = open(path, "a")
            f.close()
        except OSError:
            print("Creation of the directory %s failed" % path)

    shelf = shelve.open("../vars/")  # directory for text file to save the vars
    shelf['activation'] = False
    # shelf['active_flag'] = 0


def create_start():
    try:
        createShelfFolder()
    except:
        pass