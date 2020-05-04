import os


class Finals:
    USERNAME = os.environ['COMPUTERNAME']
    active_field = 'activation'
    command_execute = "command_execute"
    width_screen = "width"
    height_screen = "height"
    path = "../vars/vars.txt"
    first_setup_path = "../vars/"
    files_from_server_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\ControlNet_files\\'
