from tkinter import *
from socket import *
from threading import *
#from scrolledText import*
from tkinter.scrolledtext import ScrolledText
from time import sleep

from queue import Queue

conn_q = Queue()
gui_q  = Queue()

def client_recv(my_socket):
    while True:
        data = my_socket.recv(1024)
        if data=="":
            print("server close this socket")
            my_socket.close()
            break #get out from thread
        data = data.decode('latin-1')
        print ("client_recv:" + data )
        print("4444",current_thread().name)
        gui_q.put(data)

def client_send():
    print("start client")
    my_socket = socket()
    my_socket.connect(("127.0.0.1",8820))
    #my_socket.connect(("10.0.0.31",8820))

    recvThread = Thread(target=client_recv, args=(my_socket,))
    recvThread.start()

    while True:
        if conn_q.empty() == False:
            data = conn_q.get()
            print ("client_send:" + data )
            print("3333",current_thread().name)
            my_socket.sendall(data.encode('latin-1'))
        sleep(0.05) #sleep a little before check the queue again






        
class App(Thread):
 
  def __init__(self, master):
  
    commThread = Thread(target= client_send, args=())
    commThread.start()
  
    Thread.__init__(self)
    frame = Frame(master)
    frame.pack()
    self.gettext = ScrolledText(frame, height=10,width=100)
    self.gettext.pack()
    self.gettext.insert(END,'Welcome to Chat\n')
    self.gettext.configure(state='disabled')
    sframe = Frame(frame)
    sframe.pack(anchor='w')
    self.pro = Label(sframe, text="Client>>");
    self.sendtext = Entry(sframe,width=80)
    self.sendtext.focus_set()
    self.sendtext.bind(sequence="<Return>", func=self.Send)
    self.pro.pack(side=LEFT)
    self.sendtext.pack(side=LEFT)
    
  def Send(self, args):
    print("2222",current_thread().name)
    self.gettext.configure(state='normal')
    text = self.sendtext.get()
    if text=="": text=" "
    self.gettext.insert(END,'Me >> %s\n'%text)
    self.sendtext.delete(0,END)
    conn_q.put(text)
    
    self.sendtext.focus_set()
    self.gettext.configure(state='disabled')
    self.gettext.see(END)
  def run(self):
    while True:
        if gui_q.empty() == False:
            text = gui_q.get()
        
            print("1111",current_thread().name)
            self.gettext.configure(state='normal')
            self.gettext.insert(END,'Server >> %s\n'%text)
            self.gettext.configure(state='disabled')
            self.gettext.see(END)
        sleep(0.05) #sleep a little before check the queue again
      
root = Tk()
root.title('Client Chat')
app = App(root).start()
root.mainloop()
