import subprocess
from subprocess import check_output
import time
import threading
from threading import Thread
import sys
import shelve
from apscheduler.schedulers.blocking import BlockingScheduler

shelf = shelve.open("../vars/")
scheduler = BlockingScheduler()


def parser(msg, keyWord):
    """
    msg - send the message got from (devcon find *) into msg
    keyWord - send the specific word to be searched
    return value is array with all the id's of the specific hardware
    """
    array = []
    msg = msg.decode()
    lines = str(msg).split("\n")
    for line in lines:
        if line.find(str(keyWord)) != -1:
            good_part = line.split(":")
            good_part = good_part[0].strip()
            array.append(good_part)
    return array


def find_all():
    msg = check_output("devcon find *")
    return msg


def callDevcon(command, array):
    """
    function to call devcon
    command - what to operate
    array - the array of ids to be operated (can be NULL)
    """
    for obj in array:
        c = "devcon " + command + " @\"" + obj + "\""
        print(c)
        output = check_output(c)
        print(output.decode())


def unlock():
    # unlock devices
    subprocess.Popen("devcon rescan")


def lock_device(KeyWord):
    # lock devices of the keyword
    while shelf['activation'] is True:
        devices = find_all()
        keyword_devices = parser(devices, KeyWord)
        if len(keyword_devices) != 0:
            callDevcon("remove", keyword_devices)
    unlock()


def lock_all():
    # lock mouse, keyboard and touch pad of the computer.
    # subprocess.Popen("devcon remove usb*")
    while shelf['activation'] is True:
        devices = find_all()
        mouse_devices = parser(devices, "mouse")
        Mouse_devices = parser(devices, "Mouse")
        touch_pad_device = parser(devices, "pad")
        keyboard_devices = parser(devices, "Keyboard")
        print("mouse")
        print(mouse_devices)
        print("Mouse")
        print(Mouse_devices)
        print("Keyboard")
        print(keyboard_devices)
        # if len(keyboard_devices) != 0:
        try:
            callDevcon("remove", keyboard_devices)
        except:
            pass
        try:
            callDevcon("remove", mouse_devices)
        except:
            pass
        try:
            callDevcon("remove", touch_pad_device)
        except:
            pass
        try:
            callDevcon("remove", Mouse_devices)
        except:
            pass
    unlock()


def main():
    lock_option = int(sys.argv[1])
    if str(lock_option) == "0":
        print("all")
        print(shelf['activation'])
        if shelf['activation'] is True:
            lock_all()
        else:
            unlock()
    else:
        print("keyboard")
        print(shelf['activation'])
        if shelf['activation'] is True:
            lock_device("Keyboard")
        else:
            unlock()


if __name__ == "__main__":
    main()
