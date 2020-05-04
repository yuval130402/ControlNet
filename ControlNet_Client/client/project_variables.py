import os
import subprocess
import shelve
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
from finals import Finals as final

"""
I had to replace shelve - in order to save vars forever (shelve doesnt work)
this are the funcs
"""


def create_vars_folder(path):
    # define the name of the directory to be created

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)
        if path == "../vars/":
            create_var(final.active_field, 0)
            create_var(final.command_execute, "")
            create_var(final.width_screen, -1)
            create_var(final.height_screen, -1)


def create_var(var, value):
    append_con = open(final.path, "a")
    append_con.write(str(var) + ',' + str(value) + "\n")
    append_con.close()


def replace(pattern, value):
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(final.path) as old_file:
            for line in old_file:
                parts = line.split(",")
                if str(parts[0]) == str(pattern):
                    new_file.write(line.replace(line, pattern + "," + str(value) + "\n"))
                else:
                    new_file.write(line)
    copymode(final.path, abs_path)
    remove(final.path)
    move(abs_path, final.path)


def get(pattern):
    read_con = open(final.path, "r+")
    content = read_con.read()
    lines = content.split("\n")
    for line in lines:
        parts = line.split(",")
        if str(parts[0]) == str(pattern):
            return parts[1].strip("\n")
    read_con.close()


"""def createShelfFolder():
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
            shelf = shelve.open("../vars/")  # directory for text file to save the vars
            shelf['activation'] = False
            shelf['active_flag'] = 0
            shelf['command_execute'] = ""
        except OSError:
            print("Creation of the directory %s failed" % path)"""


def create_start():
    try:
        create_vars_folder(final.first_setup_path)
        create_vars_folder(final.files_from_server_path)
    except:
        pass
