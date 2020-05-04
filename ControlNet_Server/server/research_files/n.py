import subprocess 
from time import sleep

"""
def lock():
	subprocess.call("devcon remove usb*")
"""
def open():
	subprocess.call("devcon rescan")


#lock()
#sleep(10)
open()