from ctypes import *
# ok = windll.user32.BlockInput(True)
# time.sleep(10)
import subprocess
import tkinter as tk
from time import sleep
import threading
from threading import Thread
import sys
import client_big_project


def lock():
    subprocess.Popen("devcon remove usb*")


def unlock():
    subprocess.Popen("devcon rescan")


def exb():
    pass


def waitingwindow():
    global stop_lock
    #  global wa
    wa = tk.Tk()
    # this removes the maximize button
    # wa.attributes("-topmost", True)
    # if stop_lock:
        # wa.destroy()
    # wa.state('zoomed')
    # wa.attributes("-topmost", True)
    wa.overrideredirect(1)
    wa.title('FUCK_YOU')
    wa.protocol("WM_DELETE_WINDOW", exb)
    wa.protocol("WM_MINIMIZE_WINDOW", exb)
    x = wa.winfo_screenwidth()
    y = wa.winfo_screenheight()
    wa.geometry("%dx%d" % (x, y))
    lb1 = tk.Label(wa, text="FUCK YOU BITCH\n", font=("Arial Bold", 70), pady=200, fg="RED")
    #  p1 = tk.Label(wa, text="YOUR COLOR: BLUE \n", font=("Arial Bold", 30), pady=40, fg="blue")
    #  p2 = tk.Label(wa, text="RIVAL COLOR: RED ", font=("Arial Bold", 30), pady=40, fg="Red")
    lb1.pack()
    #  p1.pack()
    #  p2.pack()
    wa.lift()
    # wa.mainloop()
    wa.update()


def main():
    """"n = int(sys.argv[1])
    print(n)
    if str(n) == "1":
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
        unlock()"""
    lock_thread = threading.Thread(target=waitingwindow(), args=())
    lock_thread.start()
    lock()
    sleep(6)
    unlock()


if __name__ == "__main__":
    main()
