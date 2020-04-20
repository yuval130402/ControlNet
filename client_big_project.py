__author__ = 'Yuval Cohen'
"""The main file on the client computer. Includes the Client class, 
his commands and his communication with the server."""
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
import shelve
import createvars
import getpass
from pathlib import Path
from getmac import get_mac_address as gma


from queue import Queue
from ctypes import windll
SetWindowPos = windll.user32.SetWindowPos
createvars.create_start()
shelf = shelve.open("../vars/")
USER_NAME = getpass.getuser()

NOSIZE = 1
NOMOVE = 2
TOPMOST = -1
NOT_TOPMOST = -2

prog_call = Path(__file__).absolute()
prog_call = r'%s' % str(prog_call).replace('\\', '/')
prog_location = os.path.split(prog_call)[0]
BATCH_LOCK = prog_location + "/block.bat"
BLOCK_INPUT_LOCATION = prog_location + "/block_input.py"
conn_q = Queue()
check_q = Queue()
MAX_BYTES = 65000
# SERVER_IP = '10.70.232.229'
SERVER_IP = '192.168.0.116'
MAC_ADDRESS = gma().replace(":", "")
SERVER_PORT = 9007
SECONDARY_PORT = 9562
THIRD_PORT = 15678


def add_to_startup(file_path=""):
    if file_path == "":
        file_path = prog_call
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write('cd %s/venv/Scripts/activate' % prog_location + '\n')
        bat_file.write(r'start "" %s' % os.path.split(file_path)[1])


def recv_watch():
    global watch_screen
    data, address = watch_client_socket.recvfrom(1024)
    if data.decode() == "watch_stop":
        print("kkk")
        watch_screen = False


def control_mss():
    # the function photographs the student's screen and sends it to the teacher
    global watch_screen
    watch_screen = True
    global watch_client_socket
    watch_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    watch_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    screen_size = "{},{}".format(client.WIDTH, client.HEIGHT)
    watch_client_socket.sendto(screen_size.encode(), (SERVER_IP, THIRD_PORT))
    # recv_watch_thread = threading.Thread(target=recv_watch, args=())
    # recv_watch_thread.start()
    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': client.WIDTH, 'height': client.HEIGHT}
        while watch_screen:
            try:
                img = sct.grab(rect)
                pixels = compress(img.rgb, 6)
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                size_bytes = size.to_bytes(size_len, 'big')
                watch_client_socket.sendto(size_bytes, (SERVER_IP, THIRD_PORT))
                sleep = False
                if size > 200000:
                    sleep = True
                while client.max_bytes < len(pixels):
                    part_pixels = pixels[:client.max_bytes]
                    watch_client_socket.sendto(part_pixels, (SERVER_IP, THIRD_PORT))
                    if sleep:
                        time.sleep(0.001)
                    pixels = pixels[client.max_bytes:]
                watch_client_socket.sendto(pixels, (SERVER_IP, THIRD_PORT))
            except:
                pass
            time.sleep(0.01)
    print("end")
    watch_client_socket.close()


def control_mouse(data):
    # gets the position of the teacher's mouse and change the mouse to this position
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
    # create a connection with the server mouse socket,
    # loop of recieves the position of the teacher's mouse and change the mouse to this position
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
    # create a window showing 'lock computer'
    wa = tk.Tk()
    # this removes the maximize button
    wa.state('zoomed')
    wa.attributes("-topmost", True)
    wa.overrideredirect(1)
    wa.title('YOUR COMPUTER IS LOCKED')
    wa.protocol("WM_DELETE_WINDOW", exb)
    wa.protocol("WM_MINIMIZE_WINDOW", exb)
    x = wa.winfo_screenwidth()
    y = wa.winfo_screenheight()
    wa.geometry("%dx%d" % (x, y))
    lb1 = tk.Label(wa, text="YOUR COMPUTER IS LOCKED\n", font=("Arial Bold", 70), pady=200, fg="RED")
    lb1.pack()
    wa.lift()
    # wa.mainloop()
    wa.update()
    while shelf['activation'] is True:
        time.sleep(0.1)
    print("destroy")
    wa.destroy()


def run_batch(param):
    # run the batch file with the parameter it gets
    os.system(BATCH_LOCK + " " + BLOCK_INPUT_LOCATION + " " + param)


def client_send():
    # The function is responsible for sending information from the client
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
        self.mac = MAC_ADDRESS
        self.mouse = MouseController()
        self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        send_thread = threading.Thread(target=client_send, args=())
        send_thread.start()

    def socket_send(self, conn_socket, message):
        # gets the socket object and the message to send, and send it to the server.
        connection_address_port = (self.server_ip, self.port)
        conn_socket.sendto(message.encode(), connection_address_port)

    def socket_recv(self, conn_socket, msgsize):
        # gets the socket object and the max size of recv, returns the recieved message.
        full_message, address = conn_socket.recvfrom(msgsize)
        return full_message

    def recvall(self, length):
        # gets the size(length) of the picture, returns the pixels of the picture.
        buf = b''
        while len(buf) < length:
            data = self.client_socket.recvfrom(self.max_bytes)
            data = data[0]
            if not data:
                return data
            buf += data
        return buf

    def recieve_screen(self):
        # display on the client's screen the screen of the server.
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
                alwaysOnTop(True)
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
            print("pygame quit")
            shelf['activation'] = False
            pygame.quit()
            self.client_socket.settimeout(None)
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
        # gets a string of the selected command and handle it.
        if command == "send_screen":
            mouse_thread = threading.Thread(target=show_mouse, args=())
            mouse_thread.start()
            shelf['activation'] = True
            run1_thread = threading.Thread(target=run_batch, args="1")
            run1_thread.start()
            self.recieve_screen()
        if command == "lock_screen":
            print("lock")
            shelf['activation'] = True
            run2_thread = threading.Thread(target=run_batch, args="0")
            run2_thread.start()
            time.sleep(0.5)
            lock_thread = threading.Thread(target=waitingwindow, args=())
            lock_thread.start()
            # self.lock_screen(True)
        if command == "unlock_screen":
            print("unlock")
            shelf['activation'] = False
            # os.system(BATCH_LOCK + " 0")
            # self.lock_screen(False)
        if command == "turn_off_computer":
            print("turn off computer")
            time.sleep(1)
            os.system('shutdown /p /f')
        if command == "watch_screen":
            print("watch_screen")
            time.sleep(0.5)
            watch_thread = threading.Thread(target=control_mss, args=())
            watch_thread.start()
            # control_mss()

    def run(self):
        # runs client listening.
        global watch_screen
        self.client_socket.sendto("new client".encode(), (self.server_ip, self.port))
        data, address = self.client_socket.recvfrom(self.max_bytes)
        if data.decode() != "connected":
            computer_name = str(input("enter your computer name/number"))
            while True:
                computer_data = ("new client" + computer_name + "    " + self.mac).encode()
                self.client_socket.sendto(computer_data, (self.server_ip, self.port))
                data, address = self.client_socket.recvfrom(self.max_bytes)
                if data.decode() == "welcome":
                    break
                computer_name = str(input(data.decode()))

        if shelf['command_execute'] != "":
            if shelf['command_execute'] == "lock_screen":
                self.command_response("lock_screen")
            if shelf['command_execute'] == "lock_screen":
                self.command_response("unlock_screen")
        while True:
            try:
                print("run")
                data, address = self.client_socket.recvfrom(self.max_bytes)
                print(data)
                data = data.decode()
                if data == "watch_stop":
                    watch_screen = False
                # if data.startswith("command"):
                self.command_response(data)
            except:
                pass


def main():
    add_to_startup()
    global client
    client = Client(MAX_BYTES)
    client.start()


if __name__ == '__main__':
    main()
