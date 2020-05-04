from socket import socket
import socket
from zlib import decompress
import pythoncom
import pygame
import ctypes
from ctypes import *
import time
import win32gui
import win32con


user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)
MAX_BYTES = 65000

"""def hide_tool_bar(a=False):
    # hide the tool bar
    if a:
        hwnd = win32gui.FindWindow("Shell_traywnd", None)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    else:
        hwnd = win32gui.FindWindow("Shell_traywnd", None)
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE) """


def socket_send(conn_socket, message):
    connection_address_port = ('127.0.0.1', 1061)
    conn_socket.sendto(message.encode(), connection_address_port)


def socket_recv(conn_socket, msgsize):
    full_message, address = conn_socket.recvfrom(msgsize)
    return full_message


def uMad(event):
    return False


def uMad2(event):
    return True


def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recvfrom(MAX_BYTES)
        data = data[0]
        if not data:
            return data
        buf += data
    return buf


def main():
    # sock = socket.socket()
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # sock.connect((host, port))
    # data = sock.recv(1024).decode()
    sock.sendto("gghvg".encode(), ('192.168.0.127', 1061))
    # print("a")
    data = socket_recv(sock, 1024).decode()
    width, height = data.split(",")
    # print(width, height)
    width = int(width)
    height = int(height)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    watching = True
    # ctypes.windll.user32.LockWorkStation() lock the user
    try:
        # hide_tool_bar()
        # pygame.mouse.set_visible(False)
        # ok = windll.user32.BlockInput(True) lock keyboard
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    watching = False
                    break

            size = int.from_bytes(socket_recv(sock, MAX_BYTES), byteorder='big')
            while size > 10000000:
                size = int.from_bytes(socket_recv(sock, MAX_BYTES), byteorder='big')
            # print(size)
            temp_pixels = recvall(sock, size)
            try:
                pixels = decompress(temp_pixels)
                # Create the Surface from raw pixels
                img = pygame.image.fromstring(pixels, (width, height), 'RGB')
                picture = pygame.transform.scale(img, (WIDTH, HEIGHT))
                # Display the picture
                screen.blit(picture, (0, 0))
                pygame.display.flip()
                clock.tick(60)
            except Exception:
                print("1")
                pass

    finally:
        # hide_tool_bar(True)
        # pygame.mouse.set_visible(True)
        # ok = windll.user32.BlockInput(False)
        sock.close()


if __name__ == '__main__':
    main()
