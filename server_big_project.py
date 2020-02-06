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


clients = set()
MAX_BYTES = 65000
SERVER_IP = '0.0.0.0'
BROADCAST_IP = '10.70.235.255'
SERVER_PORT = 9006


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

    def select_client_by_id(self, client_id):
        conn = sqlite3.connect('Clients.db')
        strsql = "SELECT * from " + self.__tablename + " where " \
                 + self.__clientId + "=" + "'" + str(client_id) + "'"
        cursor = conn.execute(strsql)
        rows = cursor.fetchall()
        # type(cursor) is  'sqlite3.Cursor' ,type(rows) is 'list'
        if len(rows) == 0:
            conn.close()
            return False
        conn.close()
        return True


"""def broadcast(msg):
    Broadcasts a message to all the clients.
    for sock in clients:
        # sock.send(bytes(prefix, "utf8") + msg)
        sock.send(msg.encode('ascii'))


def handle_client(client_socket):  # Takes client socket as argument.
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


def command_click():
    if common.task_command == "send_screen":
        gui_q()
        manager.server_socket.sendto("send_screen".encode(), manager.address)
        manager.send_screen(manager.address)
    if common.task_command == "lock_screen":
        manager.server_socket.sendto("lock_screen".encode(), manager.address)


class Server(Thread):
    def __init__(self, max_bytes):
        Thread.__init__(self)
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)
        self.max_bytes = max_bytes
        self.server_ip = SERVER_IP
        self.broadcast_ip = BROADCAST_IP
        self.port = SERVER_PORT
        self.address = ""
        # create socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket.bind((self.server_ip, self.port))
        print('Listening at {}'.format(self.server_socket.getsockname()))

    def run(self):
        while True:
            data, self.address = self.server_socket.recvfrom(self.max_bytes)
            data = data.decode()
            if data == "hello from client":
                print("1")
                clients.add(self.address)
            else:
                """for i in clients:
                s.sendto('{0} send {1}'.format(address, data) , i )"""
                thread = Thread(target=self.send_screen())
                thread.start()
            time.sleep(0.01)

    def send_screen(self, address):
        print("77")
        with mss() as sct:
            rect = {'top': 0, 'left': 0, 'width': self.WIDTH, 'height': self.HEIGHT}
            screen_size = "{},{}".format(self.WIDTH, self.HEIGHT)
            self.server_socket.sendto(screen_size.encode(), address)
            print("22")
            while True:
                img = sct.grab(rect)
                pixels = compress(img.rgb, 6)
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                size_bytes = size.to_bytes(size_len, 'big')
                self.server_socket.sendto(size_bytes, address)
                sleep = False
                if size > 200000:
                    sleep = True
                while self.max_bytes < len(pixels):
                    part_pixels = pixels[:self.max_bytes]
                    self.server_socket.sendto(part_pixels, address)
                    if sleep:
                        time.sleep(0.01)
                    pixels = pixels[self.max_bytes:]
                self.server_socket.sendto(pixels, address)
                time.sleep(0.01)


def main():
    """"global students

    students = Clients()
    if students.insert_client("yuvalcohen", "yuval123") is False:
        students.insert_client("yosicohen", "yosi1234")

    global a
    a = Server(8822)
    a.go()"""
    global manager
    manager = Server(MAX_BYTES)
    manager.start()


if __name__ == '__main__':
    main()
