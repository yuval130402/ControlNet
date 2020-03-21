from ctypes import *
# ok = windll.user32.BlockInput(True)
# time.sleep(10)
import subprocess
import tkinter as tk
from time import sleep
import threading
from threading import Thread
import sys
import shelve
from apscheduler.schedulers.blocking import BlockingScheduler
import client_big_project

shelf = shelve.open("../vars/")
scheduler = BlockingScheduler()


def lock():
    subprocess.Popen("devcon remove usb*")


def unlock():
    subprocess.Popen("devcon rescan")


def main():
    print(shelf['activation'])
    if shelf['activation'] is True:
        lock()
    else:
        unlock()

    # scheduler.add_job(option_lock, 'cron', second="0,10,20,30,40,50")  # replace if want to 0,30
    # scheduler.start()
    """n = int(sys.argv[1])
    if str(n) == "1":
        lock()
        lock_thread = threading.Thread(target=lock(), args=())
        lock_thread.start()
        waitingwindow()
        while True:
            if client_big_project.check_q.empty() is False:
                co = client_big_project.check_q.get()
                print(co)
                print("h")
                if co == "unlock":
                    unlock()
            sleep(0.1)
    else:
        unlock()
    lock_thread = threading.Thread(target=waitingwindow(), args=())
    lock_thread.start()
    lock()
    sleep(6)
    unlock()
    sleep(5)"""


if __name__ == "__main__":
    main()
