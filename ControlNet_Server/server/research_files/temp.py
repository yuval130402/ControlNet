import pythoncom, pyWinhook
import win32gui
import win32con
import win32api
import ctypes
from ctypes import *
from PIL import Image, ImageDraw
import socket
from datetime import datetime

MAX_BYTES = 65535


def recv1(sock):
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        print(data)


def client(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    text = 'The time is {}'.format(datetime.now())
    data = text.encode()
    sock.sendto(data, ('10.70.233.58', port))
    print('The OS assigned me the address {}'.format(sock.getsockname()))
    data, address = sock.recvfrom(MAX_BYTES)  # Danger! See Chapter 2
    text = data.decode()
    print('The server {} replied {!r}'.format(address, text))
    recv1(sock)


client(1060)

"""f = win32gui.GetCursorPos()
x, y = win32api.GetCursorPos()
print(x, y)
op, handle_icon, pp = win32gui.GetCursorInfo()
print(op, handle_icon, pp)
"""#def uMad(event):
  #  return False
"""
hm = pyWinhook.HookManager()
hm.MouseAll = uMad
hm.KeyAll = uMad
hm.HookMouse()
hm.HookKeyboard()
pythoncom.PumpMessages()"""

# windll.user32.DrawIcon(x, y, handle_icon)


"""msgFromClient = "Hello UDP Server"
bytesToSend = str.encode(msgFromClient)
serverAddressPort = ("10.70.233.58", 20002)
bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = "Message from Server {}".format(msgFromServer[0])
print(msg)"""