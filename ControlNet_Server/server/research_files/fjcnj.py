import tkinter as tk
import socket
import pythoncom, pyWinhook
import time
from threading import Thread
import keyboard
import time
#  import tkinter.messagebox as tkMessageBox

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

""" this will able to exit
def exb():
    global wa
    if tkMessageBox.askokcancel('Leave', 'Are you sure you want to leave?'):
        # wa.destroy()
        pass
"""


def exb():
    pass


def uMad(event):
    return False

def uMad2(event):
    return True


def waitingwindow():
    #  global wa
    wa = tk.Tk()
    # this removes the maximize button
    wa.attributes("-topmost", True)

    wa.state('zoomed')
    wa.attributes("-topmost", True)
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
    wa.mainloop()


def main():
    waitingwindow()
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    m = s.recv(1024).decode()
    print(m)
    if m == "1":"""
    """a = Thread(target=waitingwindow)
    a.start()"""

    """hm = pyWinhook.HookManager()
    hm.MouseAll = uMad
    hm.KeyAll = uMad
    hm.HookMouse()
    hm.HookKeyboard()
    pythoncom.PumpMessages()
    time.sleep(5)
    print("bhbb")
    hm.MouseAll = uMad2
    hm.KeyAll = uMad2
    hm.UnhookMouse()
    hm.UnhookKeyboard()"""


if __name__ == "__main__":
    main()
