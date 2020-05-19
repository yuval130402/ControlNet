import os
from queue import Queue


class Finals:
    SERVER_IP = ""
    conn_q = Queue()
    check_q = Queue()
    USER_NAME = os.environ["USERNAME"]
    computer_name = os.environ['COMPUTERNAME']
    active_field = 'activation'
    command_execute = "command_execute"
    client_name = "client_name"
    width_screen = "width"
    height_screen = "height"
    path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\vars\vars.txt' % USER_NAME
    first_setup_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\vars' % USER_NAME
    main_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    # path = "../vars/vars.txt"
    # first_setup_path = "../vars/"
    files_from_server_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\ControlNet_files\\'
    error_message = ""
    end_gui = False

