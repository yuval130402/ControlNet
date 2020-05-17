__author__ = 'Yuval Cohen'
"""The main file on the teacher's computer. 
Includes the server, its functions and its communication with the clients."""
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
from server_globals import common as common
import time
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
import pygame
import os
import tkinter as tk
from tkinter import filedialog
import subprocess
import ipaddress

clients = set()
SERVER_IP = '0.0.0.0'
BROADCAST_IP = '10.70.235.252'
# BROADCAST_IP = '10.70.235.255'
SERVER_PORT = 9007
SECONDARY_PORT = 9562
THIRD_PORT = 15678
TCP_PORT = 9001
TCP_PORT2 = 9005
BUFFER_SIZE = 1024
MAX_BYTES = 65000
NETMASK = '255.255.252.0'
files_from_clients_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\ControlNet_files\\'


class Clients:
    # The class represents the database of the system clients that the manager controls.
    def __init__(self):
        # The function initializes the database
        self.__tablename = "CLIENTS"
        self.__name = "Name"
        self.__ip = "IP"
        self.__macaddress = "MAC"
        conn = sqlite3.connect('Clients.db')
        print("Opened database successfully")
        str_create = "CREATE TABLE IF NOT EXISTS " + self.__tablename + "("
        str_create += " " + self.__name + " TEXT  PRIMARY KEY    NOT NULL ,"
        str_create += " " + self.__ip + " TEXT    NOT NULL ,"
        str_create += " " + self.__macaddress + " TEXT    NOT NULL )"
        # conn.execute("drop table CLIENTS")
        conn.execute(str_create)
        print("CLIENTS created successfully")
        conn.commit()
        conn.close()

    def __str__(self):
        return "table name is ", self.__tablename

    def get_table_name(self):
        # return the database name.
        return self.__tablename

    def insert_client(self, name, ip, mac):
        # gets a specific client's name and ip, the function insert the client to the database.
        conn = sqlite3.connect('Clients.db')
        str_insert = "INSERT INTO " + self.__tablename + " (" \
                     + self.__name + "," + self.__ip + "," + self.__macaddress + ") VALUES (" \
                     + "'" + name + "'" + "," + "'" + ip + "'" + "," + "'" + mac + "'" + ");"
        print(str_insert)
        conn.execute(str_insert)
        conn.commit()
        conn.close()
        print("Record created successfully")

    def select_client_by_name(self, name):
        # gets a specific client's name, returns True if it exists in the database, False if not.
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

    def return_client_by_name(self, name):
        # gets a specific client's name, returns an array of a record with this name.
        conn = sqlite3.connect('Clients.db')
        strsql = "SELECT * from " + self.__tablename + " where " \
                 + self.__name + "=" + "'" + str(name) + "'"
        print(strsql)
        cursor = conn.execute(strsql)
        rows = cursor.fetchall()
        # type(cursor) is  'sqlite3.Cursor' ,type(rows) is 'list'
        conn.close()
        return rows

    def select_client_by_ip(self, ip_address):
        # gets a specific client's ip, returns True if it exists in the database, False if not.
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

    def return_client_by_ip(self, ip_address):
        # gets a specific client's ip, returns an array of a record with this ip.
        conn = sqlite3.connect('Clients.db')
        strsql = "SELECT * from " + self.__tablename + " where " \
                 + self.__ip + "=" + "'" + str(ip_address) + "'"
        print(strsql)
        cursor = conn.execute(strsql)
        rows = cursor.fetchall()
        # type(cursor) is  'sqlite3.Cursor' ,type(rows) is 'list'
        conn.close()
        print(rows)
        return rows

    def delete_clients(self):
        # delete all the rows in the CLIENTS table.
        conn = sqlite3.connect('Clients.db')
        c = conn.cursor()
        strsql = "DELETE FROM " + self.__tablename
        print(strsql)
        c.execute(strsql)
        print('We have deleted', c.rowcount, 'records from the table.')
        # commit the changes to db
        conn.commit()
        # close the connection
        conn.close()


class ClientThread(Thread):
    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print(" New thread started for "+ip+":"+str(port))

    def run(self):
        try:
            print(filename)
            self.sock.send(filename.encode())
            f = open(filename, 'rb')
            while True:
                l = f.read(BUFFER_SIZE)
                while (l):
                    self.sock.send(l)
                    #print('Sent ',repr(l))
                    l = f.read(BUFFER_SIZE)
                if not l:
                    f.close()
                    self.sock.close()
                    break
        except:
            pass


def send_files():
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((SERVER_IP, TCP_PORT))
    tcpsock.settimeout(6)
    threads = []

    while True:
        try:
            tcpsock.listen(50)
            print("Waiting for incoming connections...")
            (conn, (ip, port)) = tcpsock.accept()
            print('Got connection from ', (ip, port))
            newthread = ClientThread(ip, port, conn)
            newthread.start()
            threads.append(newthread)
        except:
            break

    for t in threads:
        t.join()
    print("tcp socket close")
    tcpsock.close()


def send_broadcast(sock, data):
    # gets the socket object and the send data, sends the data to all the clients in the system.
    for a in clients:
        sock.sendto(data, a)


def send_selected_clients(sock, cl, data):
    # gets the socket object, an array of selected clients and the send data,
    # sends the data to the selected clients.
    for a in cl:
        sock.sendto(data, a)


def control_mss(selected_clients_list):
    # The function receives a student list, it photographs the teacher's screen
    # and sends it to the list of selected students by the teacher.
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
    # The function listens to the mouse movements of the teacher
    # and sends the mouse position to the selected students computers
    def on_move(x, y):
        if common.picture_flag == 0:
            mouse_listener.stop()
            send_selected_clients(mouse_server_socket, selected_clients_mouse, "stop_mouse".encode())
            # mouse_server_socket.close()
        else:
            data = "{},{}".format(x, y).encode()
            send_selected_clients(mouse_server_socket, selected_clients_mouse, data)

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
    mouse_server_socket.settimeout(5)
    mouse_recv_thread = Thread(target=mouse_recv, args=())
    mouse_recv_thread.start()
    # create listeners
    with MouseListener(on_move=on_move) as mouse_listener:
        # start listeners
        mouse_listener.join()


def socket_recv(conn_socket, msgsize):
    # gets the socket object and the max size of the recieve message,
    # returns the message that gets from the client.
    full_message, address = conn_socket.recvfrom(msgsize)
    return full_message


def recvall(length):
    # gets the size(length) of the picture, returns the pixels of the picture.
    buf = b''
    while len(buf) < length:
        data = watch_server_socket.recvfrom(MAX_BYTES)
        data = data[0]
        if not data:
            return data
        buf += data
    return buf


def recieve_screen(clients_list):
    # the function gets an array of selected clients,
    # displays on the manager's screen the screen of the client that he selected.
    global watch_server_socket
    global start_watch_socket
    start_watch_socket = 1
    watch_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    watch_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    watch_server_socket.bind((SERVER_IP, THIRD_PORT))
    try:
        data, watch_address = watch_server_socket.recvfrom(1024)
        print(data)
        print(watch_address)
        data = data.decode()
        width, height = data.split(",")
        manager.width = int(width)
        manager.height = int(height)
    except:
        pass
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
            try:
                size = int.from_bytes(socket_recv(watch_server_socket, MAX_BYTES), byteorder='big')
                # print("1")
                while size > 10000000:  # checks if it size and not part of the pixels
                    size = int.from_bytes(socket_recv(watch_server_socket, MAX_BYTES), byteorder='big')

                temp_pixels = recvall(size)
                pixels = decompress(temp_pixels)
                # Create the Surface from raw pixels
                img = pygame.image.fromstring(pixels, (manager.width, manager.height), 'RGB')
                picture = pygame.transform.scale(img, (manager.WIDTH, manager.HEIGHT))
                # Display the picture
                screen.blit(picture, (0, 0))
                pygame.display.flip()
                clock.tick(60)
            except:
                pass
    finally:
        print("quit watch screen")
        pygame.quit()
        watch_server_socket.close()
        pass


def turn_on_computers(clients_list):
    turn_on_path = ".\\"
    with open(turn_on_path + "WakeOnLan.bat", "w+") as turn_on_file:
        for client_ip in clients_list:
            client_ip = client_ip[0]
            client_data = clients_table.return_client_by_ip(client_ip)
            client_mac = client_data[0][2]
            turn_on_file.write('wolcmd ' + client_mac + ' ' + client_ip + ' ' + NETMASK + ' 7')
    os.system(turn_on_path + "WakeOnLan.bat")


def selected_client_address(client_ip):
    # the function gets string of client's ip and return tuple of client address if it exists.
    for x in clients:
        if x[0] == client_ip:
            return x
    return "Wrong"


def selected_clients_from_their_names(selected_names):
    # the function gets an array of the names of selected students
    # returns an array of the clients selected addresses.
    clients_selects = []
    for name in selected_names:
        client_data = clients_table.return_client_by_name(name)
        client_ip = client_data[0][1]
        client_address = selected_client_address(client_ip)
        if client_address != "Wrong":
            clients_selects.append(client_address)
    print(clients_selects)
    return clients_selects


def send_commands():
    # The function is responsible for routing to the action selected
    # by the manager and sending it to the selected students.
    print("send commands started")
    global start_ss  # acts I should command before start send screen
    start_ss = True
    global start_mouse_socket, end_server
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
                    selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                    mouse_listener_thread = threading.Thread(target=mouse_listener, args=())
                    mouse_listener_thread.start()
                    da = "send_screen".encode()
                    send_selected_clients(manager.server_socket, selected_clients_list, da)
                    time.sleep(0.2)
                    screen_size = "{},{}".format(manager.WIDTH, manager.HEIGHT)
                    send_selected_clients(manager.server_socket, selected_clients_list, screen_size.encode())
                print("send_screen")
                control_mss(selected_clients_list)
            elif data == "send_stop":
                print("stop send screen")
                start_ss = True
                send_selected_clients(manager.server_socket, selected_clients_list, "send_stop".encode())
            elif data == "lock":
                print("lock screen")
                selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                da = "lock_screen".encode()
                send_selected_clients(manager.server_socket, selected_clients_list, da)
                # manager.server_socket.sendto("lock_screen".encode(), manager.address)
            elif data == "unlock":
                print("unlock screen")
                selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                da = "unlock_screen".encode()
                send_selected_clients(manager.server_socket, selected_clients_list, da)
            elif data == "turn_on":
                print("turn on")
                selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                turn_on_computers(selected_clients_list)
            elif data == "turn_off":
                print("turn off")
                selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                da = "turn_off_computer".encode()
                send_selected_clients(manager.server_socket, selected_clients_list, da)
            elif data == "watch_screen":
                selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                send_selected_clients(manager.server_socket, selected_clients_list, "watch_screen".encode())
                recieve_screen(selected_clients_list)
            elif data == "send_file":
                print("send file")
                file_explorer_root = tk.Tk()
                file_explorer_root.withdraw()
                global filename
                filename = filedialog.askopenfilename(filetypes=[("all files", "*")])
                if filename != "":
                    send_files_thread = threading.Thread(target=send_files, args=())
                    send_files_thread.start()
                    selected_clients_list = selected_clients_from_their_names(common.selected_clients)
                    send_selected_clients(manager.server_socket, selected_clients_list, "send_file".encode())
            elif data == "system_quit":
                send_broadcast(manager.server_socket, "system_quit".encode())
                clients_table.delete_clients()
                end_server = True
                manager.server_socket.close()
                break
        time.sleep(0.01)


class getfileThread(Thread):
    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.path = files_from_clients_path
        print(" New thread started for "+ip+":"+str(port))

    def run(self):
        client_name = self.sock.recv(BUFFER_SIZE).decode()
        print(client_name)
        file_path = self.sock.recv(BUFFER_SIZE).decode()
        print(file_path)
        file_name = os.path.split(file_path)[1]
        self.path = self.path + client_name + "\\"
        create_vars_folder(self.path)
        print(file_name)
        print(self.path)
        with open(self.path + file_name, 'wb') as f:
            print('file opened')
            while True:
                # print('receiving data...')
                data = self.sock.recv(BUFFER_SIZE)
                # print('data=%s', (data))
                if not data:
                    f.close()
                    print('file close()')
                    break
                # write data to a file
                f.write(data)


def get_file():
    global end_server
    end_server = False
    server_getfile_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_getfile_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_getfile_sock.bind((SERVER_IP, TCP_PORT2))
    server_getfile_sock.settimeout(6)
    threads = []

    while True:
        try:
            server_getfile_sock.listen(50)
            print("Waiting for incoming connections...")
            (conn, (ip, port)) = server_getfile_sock.accept()
            print('Got connection from ', (ip, port))
            newthread = getfileThread(ip, port, conn)
            newthread.start()
            threads.append(newthread)
        except:
            if end_server is True:
                break
            pass

    for t in threads:
        t.join()
    print("getfile socket close")
    server_getfile_sock.close()


def create_vars_folder(path):
    # define the name of the directory to be created
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


class Server(Thread):
    def __init__(self, max_bytes):
        Thread.__init__(self)
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.WIDTH = user32.GetSystemMetrics(0)
        self.HEIGHT = user32.GetSystemMetrics(1)
        self.width = -1
        self.height = -1
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

    def appear_in_clients_list(self, new_address):
        for a in clients:
            if str(a[0]) == str(new_address[0]):
                clients.discard(a)
                clients.add(new_address)
                return True
        return False

    def add_client(self, new_address, new_name="", new_mac=""):
        # gets new address and name, insert the client to the DB if it possible.
        if clients_table.select_client_by_ip(str(new_address[0])) is False:
            if new_name == "":
                self.server_socket.sendto("enter a name".encode(), new_address)
            else:
                if clients_table.select_client_by_name(new_name) is False:
                    clients.add(new_address)
                    clients_table.insert_client(new_name, str(new_address[0]), new_mac)
                    print("client was added")
                    # common.gui_q.put(" " + new_name + "  " + str(new_address[0]))
                    common.gui_q.put(" " + new_name)
                    self.server_socket.sendto("welcome".encode(), new_address)
                    """time.sleep(0.2)
                    screen_size = "{},{}".format(self.WIDTH, self.HEIGHT)
                    self.server_socket.sendto(screen_size.encode(), new_address)"""
                else:
                    self.server_socket.sendto("This name is exist, enter other name.".encode(), new_address)
        else:
            if self.appear_in_clients_list(new_address) is False:
                clients.add(new_address)
                print("client was added")
                client_data = clients_table.return_client_by_ip(new_address[0])
                common.gui_q.put(" " + client_data[0][0])
            self.server_socket.sendto("connected".encode(), new_address)
            """time.sleep(0.2)
            screen_size = "{},{}".format(self.WIDTH, self.HEIGHT)
            self.server_socket.sendto(screen_size.encode(), new_address)"""

    def run(self):
        # run server listening.
        while True:
            try:
                data, self.address = self.server_socket.recvfrom(self.max_bytes)
                print(data)
                print(self.address)
                data = str(data.decode())
                if data.startswith("new client"):
                    if len(data) == 10:
                        self.add_client(self.address)
                    else:
                        client_data = data[10:].split("    ")
                        self.add_client(self.address, client_data[0], client_data[1])
                time.sleep(0.01)
            except OSError:
                break


def main():
    global manager
    global clients_table
    try:
        create_vars_folder(files_from_clients_path)
    except:
        pass
    getfiles_thread = Thread(target=get_file, args=())
    getfiles_thread.start()
    clients_table = Clients()
    manager = Server(MAX_BYTES)
    manager.start()


if __name__ == '__main__':
    main()
