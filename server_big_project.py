__author__ = 'Yuval Cohen'
import sqlite3
import sys
import threading
from threading import Thread
from zlib import compress
from zlib import decompress
from mss import mss
import ctypes
from socket import socket
import socket
import common
import time
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
import pygame


clients = set()
# selected_clients_list = []
MAX_BYTES = 65000
SERVER_IP = '0.0.0.0'
BROADCAST_IP = '10.70.235.255'
SERVER_PORT = 9007
SECONDARY_PORT = 9562
THIRD_PORT = 15678


class Clients:
    def __init__(self):
        self.__tablename = "CLIENTS"
        self.__clientId = "ClientId"
        self.__name = "Name"
        self.__ip = "IP"
        conn = sqlite3.connect('Clients.db')
        print("Opened database successfully")
        str_create = "CREATE TABLE IF NOT EXISTS " + self.__tablename + "(" \
                     + self.__clientId + " " + " INTEGER PRIMARY KEY AUTOINCREMENT ,"
        str_create += " " + self.__name + " TEXT    NOT NULL ,"
        str_create += " " + self.__ip + " TEXT    NOT NULL )"
        # conn.execute("drop table CLIENTS")
        conn.execute(str_create)
        print("CLIENTS created successfully")
        conn.commit()
        conn.close()

    def __str__(self):
        return "table name is ", self.__tablename

    def get_table_name(self):
        return self.__tablename

    def insert_client(self, name, ip):
        conn = sqlite3.connect('Clients.db')
        str_insert = "INSERT INTO " + self.__tablename + " (" \
                     + self.__name + "," + self.__ip + ") VALUES (" \
                     + "'" + name + "'" + "," + "'" + ip + "'" + ");"
        print(str_insert)
        conn.execute(str_insert)
        conn.commit()
        conn.close()
        print("Record created successfully")

    def select_client_by_name(self, name):
        conn = sqlite3.connect('Clients.db')
        strsql = "SELECT * from " + self.__tablename + " where " \
                 + self.__name + "=" + "'" + str(name) + "'"
        print(strsql)
        cursor = conn.execute(strsql)
        rows = cursor.fetchall()
        # type(cursor) is  'sqlite3.Cursor' ,type(rows) is 'list'
        if len(rows) == 0:
            conn.close()
            return False
        conn.close()
        return True

    def select_client_by_ip(self, ip_address):
        conn = sqlite3.connect('Clients.db')
        strsql = "SELECT * from " + self.__tablename + " where " \
                 + self.__ip + "=" + "'" + str(ip_address) + "'"
        print(strsql)
        cursor = conn.execute(strsql)
        rows = cursor.fetchall()
        # type(cursor) is  'sqlite3.Cursor' ,type(rows) is 'list'
        if len(rows) == 0:
            conn.close()
            return False
        conn.close()
        return True

"""def handle_client(client_socket):  # Takes client socket as argument.
    Handles a single client connection.
    while(1):
        client_info = client_socket.recv(1024).decode('ascii')
        if client_info == "":
            client_socket.close()
            clients.remove(client_socket)
            print("client close the socket")
            sys.exit()
            break
        client_info = client_info.split(" ")
        username = client_info[0]
        password = client_info[1]
        print(username, password)
        s = u.select_user_by_id(username, password)
        if s is True:
            welcome = "Welcome " + str(username)
            client_socket.send(welcome.encode('ascii'))
            print_products = p.select_Products()
            client_socket.send(print_products.encode('ascii'))
        else:
            client_socket.send("error".encode('ascii'))
"""


def send_broadcast(sock, data):
    for a in clients:
        sock.sendto(data, a)


def send_selected_clients(sock, cl, data):
    for a in cl:
        print(a)
        sock.sendto(data, a)


def control_mss(selected_clients_list):
    with mss() as sct:
        try:
            rect = {'top': 0, 'left': 0, 'width': manager.WIDTH, 'height': manager.HEIGHT}
            img = sct.grab(rect)
            pixels = compress(img.rgb, 6)
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            size_bytes = size.to_bytes(size_len, 'big')
            # manager.server_socket.sendto(size_bytes, address)
            send_selected_clients(manager.server_socket, selected_clients_list, size_bytes)
            sleep = False
            if size > 200000:
                sleep = True
            while manager.max_bytes < len(pixels):
                part_pixels = pixels[:manager.max_bytes]
                # manager.server_socket.sendto(part_pixels, address)
                send_selected_clients(manager.server_socket, selected_clients_list, part_pixels)
                if sleep:
                    time.sleep(0.001)
                pixels = pixels[manager.max_bytes:]
            # manager.server_socket.sendto(pixels, address)
            send_selected_clients(manager.server_socket, selected_clients_list, pixels)
            if common.picture_flag == 1:
                common.conn_q.put("send_screen")
            time.sleep(0.01)
        except:
            if common.picture_flag == 1:
                common.conn_q.put("send_screen")
            time.sleep(0.01)


def mouse_listener():
    def on_move(x, y):
        if common.picture_flag == 0:
            mouse_listener.stop()
            send_selected_clients(mouse_server_socket, selected_clients_mouse, "stop_mouse".encode())
            # mouse_server_socket.sendto("stop_mouse".encode(), addr)
            # mouse_server_socket.close()
        else:
            data = "{},{}".format(x, y).encode()
            send_selected_clients(mouse_server_socket, selected_clients_mouse, data)
            # mouse_server_socket.sendto(data.encode(), addr)

    def mouse_recv():
        global addr
        while common.picture_flag == 1:
            try:
                dconnect, addr = mouse_server_socket.recvfrom(MAX_BYTES)
                selected_clients_mouse.append(addr)
            except Exception as e:
                print(e)
    # create socket
    global start_mouse_socket
    global mouse_server_socket
    global selected_clients_mouse
    selected_clients_mouse = []
    if start_mouse_socket == 0:
        start_mouse_socket = 1
        mouse_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mouse_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mouse_server_socket.bind((SERVER_IP, SECONDARY_PORT))
    print('Listening at {}'.format(mouse_server_socket.getsockname()))
    mouse_recv_thread = Thread(target=mouse_recv, args=())
    mouse_recv_thread.start()
    # create listeners
    with MouseListener(on_move=on_move) as mouse_listener:
        # start listeners
        mouse_listener.join()


def socket_recv(conn_socket, msgsize):
    full_message, address = conn_socket.recvfrom(msgsize)
    return full_message


def recvall(length):
    buf = b''
    while len(buf) < length:
        data = watch_server_socket.recvfrom(MAX_BYTES)
        data = data[0]
        if not data:
            return data
        buf += data
    return buf


def recieve_screen(clients_list):
    global watch_server_socket
    global start_watch_socket
    start_watch_socket = 1
    watch_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    watch_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    watch_server_socket.bind((SERVER_IP, THIRD_PORT))
    data, watch_address = watch_server_socket.recvfrom(1024)
    print(data)
    print(watch_address)
    data = data.decode()
    width, height = data.split(",")
    width = int(width)
    height = int(height)
    # open the window
    pygame.init()
    screen = pygame.display.set_mode((manager.WIDTH, manager.HEIGHT))
    clock = pygame.time.Clock()
    watch_server_socket.settimeout(4)
    watching = True
    # print other computer screen
    try:
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("close")
                    watching = False
                    pygame.quit()
                    send_selected_clients(manager.server_socket, clients_list, "watch_stop".encode())
                    # watch_server_socket.sendto("watch_stop".encode(), watch_address)
                    break
            size = int.from_bytes(socket_recv(watch_server_socket, MAX_BYTES), byteorder='big')
            print("1")
            while size > 10000000:  # checks if it size and not part of the pixels
                size = int.from_bytes(socket_recv(watch_server_socket, MAX_BYTES), byteorder='big')
            temp_pixels = recvall(size)
            try:
                pixels = decompress(temp_pixels)
                # Create the Surface from raw pixels
                img = pygame.image.fromstring(pixels, (width, height), 'RGB')
                picture = pygame.transform.scale(img, (manager.WIDTH, manager.HEIGHT))
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


def send_commands():
    print("send commands started")
    global start_ss  # acts I should command before start send screen
    start_ss = True
    global start_mouse_socket
    start_mouse_socket = 0
    global start_watch_socket
    start_watch_socket = 0
    selected_clients_list = []
    while True:
        if common.conn_q.empty() is False:
            data = common.conn_q.get()
            if data == "send_screen":
                if start_ss is True:
                    start_ss = False
                    selected_clients_list = common.selected_clients
                    # manager.server_socket.sendto("send_screen".encode(), manager.address)
                    mouse_listener_thread = threading.Thread(target=mouse_listener, args=())
                    mouse_listener_thread.start()
                    da = "send_screen".encode()
                    send_selected_clients(manager.server_socket, selected_clients_list, da)
                    time.sleep(0.3)
                    screen_size = "{},{}".format(manager.WIDTH, manager.HEIGHT)
                    # manager.server_socket.sendto(screen_size.encode(), manager.address)
                    send_selected_clients(manager.server_socket, selected_clients_list, screen_size.encode())
                print("send_screen")
                control_mss(selected_clients_list)
            elif data == "send_stop":
                print("stop send screen")
                start_ss = True
                send_selected_clients(manager.server_socket, selected_clients_list, "send_stop".encode())
            elif data == "lock":
                print("lock screen")
                selected_clients_list = common.selected_clients
                da = "lock_screen".encode()
                send_selected_clients(manager.server_socket, selected_clients_list, da)
                # manager.server_socket.sendto("lock_screen".encode(), manager.address)
            elif data == "unlock":
                print("unlock screen")
                selected_clients_list = common.selected_clients
                da = "unlock_screen".encode()
                send_selected_clients(manager.server_socket, selected_clients_list, da)
            elif data == "turn_off":
                print("turn off")
                selected_clients_list = common.selected_clients
                da = "turn_off_computer".encode()
                send_selected_clients(manager.server_socket, selected_clients_list, da)
            elif data == "watch_screen":
                selected_clients_list = common.selected_clients
                send_selected_clients(manager.server_socket, selected_clients_list, "watch_screen".encode())
                recieve_screen(selected_clients_list)

        time.sleep(0.01)


class Server(Thread):
    def __init__(self, max_bytes):
        Thread.__init__(self)
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)
        self.max_bytes = max_bytes
        self.server_ip = SERVER_IP
        self.broadcast_ip = (BROADCAST_IP, 9006)
        self.port = SERVER_PORT
        self.address = ""
        # create socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket.bind((self.server_ip, self.port))
        print('Listening at {}'.format(self.server_socket.getsockname()))
        commThread = Thread(target=send_commands, args=())
        commThread.start()

    def run(self):
        global clients
        while True:
            data, self.address = self.server_socket.recvfrom(self.max_bytes)
            print(data)
            print(self.address)
            data = str(data.decode())
            """if data.startswith("new client"):
                if clients_table.select_client_by_ip(str(self.address[0])) is False:
                    if clients_table.select_client_by_name(data[10:]) is False:
                        clients.add(self.address)
                        clients_table.insert_client(data, str(self.address[0]))
                        print("client was added")
                        common.gui_q.put(data[10:] + "  " + str(self.address[0]))
                        self.server_socket.sendto("welcome".encode(), self.address)
                    else:
                        self.server_socket.sendto("enter other name".encode(), self.address)"""
            if data == "hello from client":
                clients.add(self.address)
                print("client was added")
                common.gui_q.put(self.address)
            else:
                """for i in clients:
                s.sendto('{0} send {1}'.format(address, data) , i )"""
            time.sleep(0.01)


def main():
    global manager
    global clients_table
    clients_table = Clients()
    manager = Server(MAX_BYTES)
    manager.start()


if __name__ == '__main__':
    main()
