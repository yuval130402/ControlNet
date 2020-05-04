"""This is a file for the global variables in the project
that the server files - the user interface files
(gui_project.py and gui_project_support.py) and the server file
(server_big_project.py) interact with using these variables"""
from queue import Queue


class common:
    conn_q = Queue()
    gui_q = Queue()
    picture_flag = 0
    selected_clients = []
    sharing_screen = False
