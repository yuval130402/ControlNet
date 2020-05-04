from tkinter import *
from socket import *
from threading import *
from tkinter.scrolledtext import ScrolledText
from time import sleep

from queue import Queue
flag = 1
conn_q = Queue()
gui_q  = Queue()

def server_send(client_socket, client_address):
    print ("server send start")
    global flag
    while flag == 1:
        if conn_q.empty() == False:
            data = conn_q.get()
            print ("server_send: " + data)
            print("3333",current_thread().name)
            client_socket.sendall(data.encode('latin-1'))
        sleep(0.05) #sleep a little before check the queue again

class Server(Thread):
    def __init__(self):
        global flag
        Thread.__init__(self)
        self.port = 8820
        print ("server recv start")
        self.server_socket = socket()
        self.server_socket.bind(('0.0.0.0',8820))
        self.server_socket.listen(1)
        

    def run(self):
        (client_socket, client_address) = self.server_socket.accept()
        print ("client accept from {0} at port {1}".format(client_address, self.port))
        client_socket.settimeout(3000)

        flag = 1
        sendThread = Thread(target=server_send, args=(client_socket, client_address))
        sendThread.start()
        while(1):
            try:
                client_info = client_socket.recv(1024)
            except Exception as e:
                flag = 0
                sleep(0.2) #let the server_send thread to be close
                print (e)
                client_socket.close()
                (client_socket, client_address) = self.server_socket.accept() #be ready for next client
                client_socket.settimeout(3000)
                print ("client accept from {0} at port {1}".format(client_address, self.port))
                flag = 1
                sendThread = Thread(target=server_send, args=(client_socket, client_address))
                sendThread.start()
                continue
            # if the code will not check empty string,then once the client terminate,
            # the server will continusly will get empty string
            if client_info == "":
                flag = 0
                sleep(0.2) #let the server_send thread to be close
                client_socket.close()
                print ("client close the socket")
                (client_socket, client_address) = self.server_socket.accept()
                print ("client accept from {0} at port {1}".format(client_address, self.port))
                client_socket.settimeout(3000)
                flag = 1
                sendThread = Thread(target=server_send, args=(client_socket, client_address))
                sendThread.start()
                continue
            client_info_str = client_info.decode('latin-1')
            print ("server_recv: " + client_info_str)
            print("4444",current_thread().name)
            gui_q.put(client_info_str)


    
class App(Thread):
  def __init__(self, master):
  
    #commThread = Thread(target= server_recv, args=())
    #commThread.start()
    commThread = Server()
    commThread.start()

  
   
    Thread.__init__(self)
    frame = Frame(master)
    frame.pack()
    self.gettext = ScrolledText(frame, height=10,width=100, state=NORMAL)
    self.gettext.pack()
    sframe = Frame(frame)
    sframe.pack(anchor='w')
    self.pro = Label(sframe, text="Server>>");
    self.sendtext = Entry(sframe,width=80)
    self.sendtext.focus_set()
    self.sendtext.bind(sequence="<Return>", func=self.Send)
    self.pro.pack(side=LEFT)
    self.sendtext.pack(side=LEFT)
    self.gettext.insert(END,'Welcome to Chat\n')
    self.gettext.configure(state=DISABLED)
  def Send(self, args):
    print("2222",current_thread().name)
    self.gettext.configure(state=NORMAL)
    text = self.sendtext.get()
    if text=="": text=" "
    self.gettext.insert(END,'Me >> %s \n'%text)
    self.sendtext.delete(0,END)
    conn_q.put(text)
    self.sendtext.focus_set()
    self.gettext.configure(state=DISABLED)
    self.gettext.see(END)
  def run(self):
    while 1:
        if gui_q.empty() == False:
            text = gui_q.get()     
            print("1111",current_thread().name)
            self.gettext.configure(state=NORMAL)
            self.gettext.insert(END,'client >> %s\n'%text)
            self.gettext.configure(state=DISABLED)
            self.gettext.see(END)
        sleep(0.05) #sleep a little before check the queue again
        
def main():        
    root = Tk()
    root.title('Server Chat')
    app = App(root).start()
    root.mainloop()

if __name__ == "__main__":
    main()