from subprocess import check_output
import subprocess
from project_variables import *
from finals import Finals as final


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
    msg = subprocess.check_output("devcon find *", shell=False)
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
        output = check_output(c, shell=False)
        print(output.decode())


def unlock():
    # unlock devices
    subprocess.Popen("devcon rescan")


def lock_device(KeyWord):
    # lock devices of the keyword
    try:
        while str(get(final.active_field)) == "1":
            devices = find_all()
            keyword_devices = parser(devices, KeyWord)
            if len(keyword_devices) != 0:
                callDevcon("remove", keyword_devices)
        unlock()
    except:
        unlock()


def lock_all():
    # lock mouse, keyboard and touch pad of the computer.
    # subprocess.Popen("devcon remove usb*")
    try:
        while str(get(final.active_field)) == "1":
            devices = find_all()
            mouse_devices = parser(devices, "mouse")
            Mouse_devices = parser(devices, "Mouse")
            touch_pad_device = parser(devices, "pad")
            keyboard_devices = parser(devices, "Keyboard")
            # print("mouse")
            # print(mouse_devices)
            # print("Mouse")
            # print(Mouse_devices)
            # print("Keyboard")
            # print(keyboard_devices)
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
    except:
        unlock()


def lock_settings():
    lock_option = str(get(final.command_execute))
    if lock_option == "lock_screen":
        print("all")
        if str(get(final.active_field)) == "1":
            lock_all()
        else:
            unlock()
    else:
        print("keyword")
        if str(get(final.active_field)) == "1":
            lock_device("Keyboard")
        else:
            unlock()


if __name__ == "__main__":
    lock_settings()
