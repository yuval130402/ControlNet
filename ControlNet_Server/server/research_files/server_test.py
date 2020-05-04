from socket import socket
import socket
from threading import Thread
from zlib import compress
from mss import mss
import ctypes
import win32gui
import win32con
from PIL import Image, ImageDraw
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)
print(WIDTH)
print(HEIGHT)


def retreive_screenshot(conn):
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}
        screen_size = "{},{}".format(WIDTH, HEIGHT)
        conn.send(screen_size.encode())
        while True:
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 6)
            try:
                # Send the size of the pixels length

                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                conn.send(bytes([size_len]))

                # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')
                conn.send(size_bytes)

                # Send pixels
                conn.sendall(pixels)
            except Exception:
                sock.close()


def main(host='0.0.0.0', port=5051):
    global sock
    sock = socket.socket()
    sock.bind((host, port))
    try:
        sock.listen(5)
        print('Server started.')

        while True:
            conn, addr = sock.accept()
            print('Client connected IP:', addr)
            thread = Thread(target=retreive_screenshot, args=(conn,))
            thread.start()
    finally:
        sock.close()


if __name__ == '__main__':
    main()
