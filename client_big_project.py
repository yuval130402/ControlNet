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
import common

MAX_BYTES = 65000
SERVER_IP = '10.70.232.229'
SERVER_PORT = 9006


class Client(Thread):
    def __init__(self, max_bytes):
        Thread.__init__(self)
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)
        self.max_bytes = max_bytes
        self.server_ip = SERVER_IP
        self.port = SERVER_PORT
        self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self.send_thread = threading.Thread(target=self.open_window)
        # self.send_thread.start()

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
        width, height = data.split(",")
        width = int(width)
        height = int(height)
        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        watching = True
        try:
            while watching:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        watching = False
                        break
                size = int.from_bytes(self.socket_recv(self.client_socket, self.max_bytes), byteorder='big')
                while size > 10000000:
                    size = int.from_bytes(self.socket_recv(self.client_socket, self.max_bytes), byteorder='big')
                temp_pixels = self.recvall(size)
                try:
                    pixels = decompress(temp_pixels)
                    # Create the Surface from raw pixels
                    img = pygame.image.fromstring(pixels, (width, height), 'RGB')
                    picture = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                    # Display the picture
                    screen.blit(picture, (0, 0))
                    pygame.display.flip()
                    clock.tick(60)
                except:
                    pass
        finally:
            self.client_socket.close()

    def exb(self):
        pass

    def uMad(self, event):
        return False

    def lock_screen(self):
        hm = pyWinhook.HookManager()
        hm.MouseAll = self.uMad
        hm.KeyAll = self.uMad
        hm.HookMouse()
        hm.HookKeyboard()
        pythoncom.PumpMessages()


    def command_response(self, command):
        if command == "send_screen":
            self.recieve_screen()
        if command == "lock_screen":
            self.lock_screen()


    def run(self):
        self.client_socket.sendto("hello from client".encode(), (self.server_ip, self.port))
        while True:
            try:
                data, address = self.client_socket.recvfrom(self.max_bytes)
                print(data)
                data = data.decode()
                self.command_response(data)
            except:
                pass


def main():
    global client
    client = Client(MAX_BYTES)
    client.start()


if __name__ == '__main__':
    main()
