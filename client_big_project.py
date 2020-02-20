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

from queue import Queue

conn_q = Queue()
MAX_BYTES = 65000
# SERVER_IP = '10.70.232.229'
SERVER_IP = '192.168.0.109'
SERVER_PORT = 9006
SECONDARY_PORT = 9561


def control_mouse(data):
    if len(data) == 2:
        x1, y1 = data
        x, y = change_xy(x1, y1)
        client.mouse.position = (int(x), int(y))


def change_xy(x, y):
    # adjust x and y size to the other computer size
    x = int(x * prop_x)
    y = int(y * prop_y)
    return x, y


def show_mouse():
    while client.width == -1:  # wait for recieve_screen and then start the listeners
        pass
    global prop_x, prop_y
    prop_x = client.width / client.WIDTH
    prop_y = client.height / client.HEIGHT
    mouse_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    mouse_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        data, address = mouse_client_socket.recvfrom(MAX_BYTES)
        data = data.decode()
        data = data.split(",")
        control_mouse(data)


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
        data = self.socket_recv(self.client_socket, 1024).decode()
        print(data)
        self.width, self.height = data.split(",")
        self.width = int(self.width)
        self.height = int(self.height)
        # open the window
        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        watching = True
        # print other computer screen
        try:
            while watching:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        watching = False
                        break
                size = int.from_bytes(self.socket_recv(self.client_socket, self.max_bytes), byteorder='big')
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
            """self.client_socket.close()"""
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
            pythoncom.PumpMessages()
        else:
            hm.UnhookMouse()
            hm.UnhookKeyboard()

    def command_response(self, command):
        if command == "send_screen":
            mouse_thread = threading.Thread(target=show_mouse(), args=())
            mouse_thread.start()
            self.recieve_screen()
        if command == "lock_screen":
            self.lock_screen(True)
        if command == "unlock_screen":
            self.lock_screen(False)

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
