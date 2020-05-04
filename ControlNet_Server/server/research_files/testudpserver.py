import socket
from threading import Thread
from zlib import compress
from mss import mss
import ctypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)
MAX_BYTES = 65000


def send_messages(client_socket, address):
    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}
        screen_size = "{},{}".format(WIDTH, HEIGHT)
        client_socket.sendto(screen_size.encode(), address)
        while True:
            img = sct.grab(rect)
            pixels = compress(img.rgb, 6)
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            size_bytes = size.to_bytes(size_len, 'big')
            client_socket.sendto(size_bytes, address)
            print(pixels)
            while MAX_BYTES < len(pixels):
                part_pixels = pixels[:MAX_BYTES]
                client_socket.sendto(part_pixels, address)
                pixels = pixels[MAX_BYTES:]
            client_socket.sendto(pixels, address)


def server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    print('Listening at {}'.format(sock.getsockname()))
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        print(data.decode())
        print(address)
        thread = Thread(target=send_messages, args=(sock, address))
        thread.start()


def main():
    server(1061)


if __name__ == '__main__':
    main()
