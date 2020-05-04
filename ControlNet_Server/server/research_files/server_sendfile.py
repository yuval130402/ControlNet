import socket
from threading import Thread
import tkinter as tk
from tkinter import filedialog

TCP_IP = '0.0.0.0'
TCP_PORT = 9001
BUFFER_SIZE = 1024


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
        #file_explorer_root.mainloop()


file_explorer_root = tk.Tk()
file_explorer_root.withdraw()
# global filename
filename = filedialog.askopenfilename(filetypes=[("all files", "*")])
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
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
