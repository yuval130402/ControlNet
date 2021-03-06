#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Support module generated by PAGE version 5.2
#  in conjunction with Tcl version 8.6
#    May 11, 2020 07:47:43 PM +0300  platform: Windows NT
#    May 11, 2020 08:59:49 PM +0300  platform: Windows NT

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

from tkinter import filedialog
import threading
from threading import Thread
from socket import socket
import socket
from project_variables import *
from client_big_project import NetworkData, BUFFER_SIZE
import time

def exb():
    pass

def init(top, gui, *args, **kwargs):
    global w, top_level, root, send_btn, client_name
    w = gui
    top_level = top
    root = top
    top_level.protocol("WM_DELETE_WINDOW", exb)  # hide close button
    send_btn = w.send_button
    client_name = w.label_name
    client_name['text'] = "Name: " + str(get(final.client_name))
    top.after(100, on_after_elapsed)

def on_after_elapsed():
    global top_level
    if final.end_gui is True:
        destroy_window()
    else:
        top_level.after(1000, on_after_elapsed)

def send_files():
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((NetworkData.SERVER_IP, NetworkData.TCP_PORT2))
    try:
        tcp_client.send(get(final.client_name).encode())
        print(filename)
        time.sleep(1.5)
        tcp_client.send(filename.encode())
        f = open(filename, 'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                tcp_client.send(l)
                # print('Sent ',repr(l))
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                tcp_client.close()
                break
    except:
        pass

def upload_files(p1):
    file_explorer_root = tk.Tk()
    file_explorer_root.withdraw()
    global filename
    filename = filedialog.askopenfilename(filetypes=[("all files", "*")])
    if filename != "":
        send_files_thread = threading.Thread(target=send_files, args=())
        send_files_thread.start()
    file_explorer_root.destroy()
    # sys.stdout.flush()

def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None

if __name__ == '__main__':
    import send_gui
    send_gui.vp_start_gui()





