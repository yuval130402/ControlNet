import win32console
import win32gui
import psutil
import os
import subprocess
import time
from finals import Finals as final

#Hide the Console
#window = win32console.GetConsoleWindow()
#win32gui.ShowWindow(window, 0)

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''

    listOfProcessObjects = []

    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            # Check if process name contains the given name string.
            if processName.lower() in pinfo['name'].lower():
                listOfProcessObjects.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return listOfProcessObjects


def run_again():
    cmd = final.main_path + "\\client_big_project.exe"
    subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()


def auto_run():
    # *** Check if a process is running or not ***
    while True:
        # Check if any client_big_project.exe process was running or not.
        if checkIfProcessRunning('client_big_project.exe'):
            print('Yes a client_big_project.exe process was running')
            time.sleep(0.1)
        else:
            print('No client_big_project.exe process was running')
            run_again()


    """print("*** Find PIDs of a running process by Name ***")

    # Find PIDs od all the running instances of process that contains 'client_big_project.exe' in it's name
    listOfProcessIds = findProcessIdByName('client_big_project.exe')

    if len(listOfProcessIds) > 0:
        print('Process Exists | PID and other details are')
        for elem in listOfProcessIds:
            processID = elem['pid']
            processName = elem['name']
            processCreationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(elem['create_time']))
            print((processID, processName, processCreationTime))
    else:
        print('No Running Process found with given text')

    print('** Find running process by name using List comprehension **')

    # Find PIDs od all the running instances of process that contains 'client_big_project.exe' in it's name
    procObjList = [procObj for procObj in psutil.process_iter() if 'client_big_project.exe' in procObj.name().lower()]

    for elem in procObjList:
        print(elem)"""


try:
    import httplib
except:
    import http.client as httplib


def have_internet():
    while True:
        conn = httplib.HTTPConnection("www.google.com", timeout=5)
        try:
            conn.request("HEAD", "/")
            conn.close()
            print("True")
        except:
            conn.close()
            print("False")
        time.sleep(3)


if __name__ == '__main__':
    # auto_run()
    have_internet()


