from socket import socket
import socket
from zlib import decompress
import pythoncom, pyWinhook
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


"""def hide_tool_bar(a=False):
    # hide the tool bar
    if a:
        hwnd = win32gui.FindWindow("Shell_traywnd", None)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    else:
        hwnd = win32gui.FindWindow("Shell_traywnd", None)
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE) """


"""def uMad(event):
    return False


def lock_keyboard():
    # lock the keyboard and the mouse
    hm = pyWinhook.HookManager()
    hm.MouseAll = uMad
    hm.KeyAll = uMad
    hm.HookMouse()
    hm.HookKeyboard()
    pythoncom.PumpMessages()


def uMad2(event):
    return True


def release_keyboard():
    # release the keyboard and the mouse
    hm = pyWinhook.HookManager()
    hm.MouseAll = uMad2
    hm.KeyAll = uMad2
    hm.HookMouse()
    hm.HookKeyboard()
    pythoncom.PumpMessages()"""


def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


def main(host='10.70.232.238', port=5051):
    sock = socket.socket()
    sock.connect((host, port))
    data = sock.recv(1024).decode()
    width, height = data.split(",")
    width = int(width)
    height = int(height)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    watching = True
    # ctypes.windll.user32.LockWorkStation() lock the user

    try:
        # hide_tool_bar()
        pygame.mouse.set_visible(False)
        ok = windll.user32.BlockInput(True)
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    watching = False
                    break

            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))

            # Create the Surface from raw pixels
            img = pygame.image.fromstring(pixels, (width, height), 'RGB')
            picture = pygame.transform.scale(img, (WIDTH, HEIGHT))
            # Display the picture
            screen.blit(picture, (0, 0))
            pygame.display.flip()
            clock.tick(60)

    finally:
        # hide_tool_bar(True)
        pygame.mouse.set_visible(True)
        ok = windll.user32.BlockInput(False)
        sock.close()


if __name__ == '__main__':
    main()
