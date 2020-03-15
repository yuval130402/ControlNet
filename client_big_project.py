__author__ = 'Yuval Cohen'

import sys
import threading
from threading import Thread
from zlib import compress
from zlib import decompress
from mss import mss
import ctypes
from socket import socket
import pythoncom, pyWinhook
import socket
import pygame
import time
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
import os
import tkinter as tk
import subprocess

from queue import Queue
from ctypes import windll
SetWindowPos = windll.user32.SetWindowPos

NOSIZE = 1
NOMOVE = 2
TOPMOST = -1
NOT_TOPMOST = -2

conn_q = Queue()
check_q = Queue()
MAX_BYTES = 65000
# SERVER_IP = '10.70.232.229'
SERVER_IP = '192.168.0.115'
SERVER_PORT = 9007
SECONDARY_PORT = 9562


def control_mouse(data):
    if len(data) == 2:
        x1, y1 = data
        x, y = change_xy(x1, y1)
        client.mouse.position = (int(x), int(y))


def change_xy(x, y):
    # adjust x and y size to the other computer size
    x = int(float(x) * prop_x)
    y = int(float(y) * prop_y)
    return x, y


def show_mouse():
    while client.width == -1:  # wait for recieve_screen and then start the listeners
        time.sleep(0.1)
    global prop_x, prop_y
    prop_x = client.width / client.WIDTH
    prop_y = client.height / client.HEIGHT
    mouse_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    mouse_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    time.sleep(0.3)
    mouse_client_socket.sendto("connected".encode(), (SERVER_IP, SECONDARY_PORT))
    print("yes")
    while True:
        data, address = mouse_client_socket.recvfrom(MAX_BYTES)
        data = data.decode()
        if data == "stop_mouse":
            print("stop_send_screen")
            # check_q.put("stop_send")
            break
        data = data.split(",")
        control_mouse(data)
    mouse_client_socket.close()


def exb():
    pass


def waitingwindow():
    global stop_lock
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
    # wa.mainloop()
    if stop_lock:
        wa.destroy()
    wa.update()


def client_send():
    while True:
        if conn_q.empty() == False:
            data = conn_q.get()
            print("client_send:" + data)
            client.socket_send(client.client_socket, data)
        time.sleep(0.05)  # sleep a little before check the queue again


class Client(Thread):
    def __init__(self, max_bytes):
        Thread.__init__(self)
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.width = -1
        self.height = -1
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)
        self.max_bytes = max_bytes
        self.server_ip = SERVER_IP
        self.port = SERVER_PORT
        self.mouse = MouseController()
        self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        send_thread = threading.Thread(target=client_send, args=())
        send_thread.start()

    def socket_send(self, conn_socket, message):
        connection_address_port = (self.server_ip, self.port)
        conn_socket.sendto(message.encode(), connection_address_port)

    def socket_recv(self, conn_socket, msgsize):
        full_message, address = conn_socket.recvfrom(msgsize)
        return full_message

    def recvall(self, length):
        buf = b''
        while len(buf) < length:
            data = self.client_socket.recvfrom(self.max_bytes)
            data = data[0]
            if not data:
                return data
            buf += data
        return buf

    def recieve_screen(self):
        def alwaysOnTop(yesOrNo):
            zorder = (NOT_TOPMOST, TOPMOST)[yesOrNo]  # choose a flag according to bool
            hwnd = pygame.display.get_wm_info()['window']  # handle to the window
            SetWindowPos(hwnd, zorder, 0, 0, 0, 0, NOMOVE | NOSIZE)
        data = self.socket_recv(self.client_socket, 1024).decode()
        print(data)
        self.width, self.height = data.split(",")
        self.width = int(self.width)
        self.height = int(self.height)
        # open the window
        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        self.client_socket.settimeout(3)
        alwaysOnTop(True)
        watching = True
        # print other computer screen
        """if check_q.empty() is False:
                cc = check_q.get()
                print(cc)
                watching = False
                pygame.quit()
                break"""
        try:
            while watching:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        print("close")
                        watching = False
                        pygame.quit()
                        break
                size = int.from_bytes(self.socket_recv(self.client_socket, self.max_bytes), byteorder='big')
                print("1")
                while size > 10000000:  # checks if it size and not part of the pixels
                    size = int.from_bytes(self.socket_recv(self.client_socket, self.max_bytes), byteorder='big')
                temp_pixels = self.recvall(size)
                try:
                    pixels = decompress(temp_pixels)
                    # Create the Surface from raw pixels
                    img = pygame.image.fromstring(pixels, (self.width, self.height), 'RGB')
                    picture = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                    # Display the picture
                    screen.blit(picture, (0, 0))
                    pygame.display.flip()
                    clock.tick(60)
                except:
                    pass
        finally:
            print("11111")
            pygame.quit()
            pass

    def uMad(self, event):
        return False

    def lock_screen(self, lock):
        hm = pyWinhook.HookManager()
        if lock is True:
            hm.MouseAll = self.uMad
            hm.KeyAll = self.uMad
            hm.HookMouse()
            hm.HookKeyboard()
            #pythoncom.PumpMessages()
        else:
            hm.UnhookMouse()
            hm.UnhookKeyboard()

    def command_response(self, command):
        if command == "send_screen":
            mouse_thread = threading.Thread(target=show_mouse, args=())
            mouse_thread.start()
            self.recieve_screen()
        if command == "lock_screen":
            print("lock")
            global stop_lock
            stop_lock = False
            lock_thread = threading.Thread(target=waitingwindow(), args=())
            lock_thread.start()
            subprocess.call([r'C:\Users\Yuval\Desktop\big_project\block.bat 1'])
            # os.system(r"C:\Users\Yuval\Desktop\big_project\block.bat 1")
            # self.lock_screen(True)
        if command == "unlock_screen":
            print("unlock")
            stop_lock = True
            subprocess.call([r'C:\Users\Yuval\Desktop\big_project\block.bat 0'])
            # os.system(r"C:\Users\Yuval\Desktop\big_project\block.bat 0")
            # self.lock_screen(False)
        if command == "turn_off_computer":
            print("turn off computer")
            time.sleep(1)
            os.system('shutdown /p /f')

    def run(self):
        self.client_socket.sendto("hello from client".encode(), (self.server_ip, self.port))
        while True:
            try:
                data, address = self.client_socket.recvfrom(self.max_bytes)
                data = data.decode()
                # if data.startswith("command"):
                self.command_response(data)
            except:
                pass


def main():
    global client
    client = Client(MAX_BYTES)
    client.start()


if __name__ == '__main__':
    main()
