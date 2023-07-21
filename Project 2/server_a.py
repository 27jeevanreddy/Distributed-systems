//Name: JEEVAN REDDY BODAPATLA
//ID:1001949287

#!/usr/bin/env python3
"""
    Implementation of SERVER A
        SEVER A -> Listining IP (Default) - 127.0.0.1 PORT -  55555
        SERVER B -> Listining IP (Default) - 127.0.0.1 PORT - 55556

        on a client request SEVER A will create a thread which will do following task
            Request for Directory Status of server_b on  SERVER B
            Collect Directory Status from server_a on SERVER A
            Combine and Transform Result (such that sort data based
            on filename and will contain only required fields)
            Return Response to client
"""
# to use multithreading to access multiple clients
import threading

# To create a SERVER A socket to listen client requests
import socket

# To access files and directories
import os

# To process bytes data
import json

# custom module to get list of files from a directory
from myutils import get_list

# watchdog to observe file-system events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# To delete and copy file
from os import remove as rmf
from shutil import copyfile as cpf

# To pretty print errors
from pprint import pprint

# Directory paths on SERVER A & B to list data
SERVER_A_DIR = os.path.join(os.getcwd(), "server_a_dir")
SERVER_B_DIR = os.path.join(os.getcwd(), "server_b_dir")

# SERVER DEFAULT CONFIGS
SERVER_A_IP = socket.gethostbyname(socket.gethostname())
SERVER_B_IP = socket.gethostbyname(socket.gethostname())
SERVER_A_PORT = 55555
SERVER_B_PORT = 55556

MAX_CONCURRENT_CONNECTIONS = 5
MAX_BYTES_SIZE = 2048

class SERVER:
    """
        Implementation of Server A
    """
    def __init__(self):
        """Default Parameters"""
        self.initlize()

    def initlize(self):
        """initlize server socket"""
        self.socket = socket.socket()
        # creating a server socket
        self.socket.bind((SERVER_A_IP, SERVER_A_PORT))
        # binding server socket to SERVER A's IP and Port
        self.socket.listen(MAX_CONCURRENT_CONNECTIONS)
        temp = "INFO    SERVER A is Ready to Handle Client Request"
        temp += f"at {SERVER_A_IP}:{SERVER_A_PORT}"
        print(temp)
        # SERVER A is ready to Listen Clients

    @staticmethod
    def process_request(csocket, client_ip, client_port):
        """
        method which will do all work as follow
            first it will connect to SERVER_B and access files from SERVER B
        """
        temp_socket = socket.socket()
        temp_socket.connect((SERVER_B_IP, SERVER_B_PORT))
        temp_socket.send(SERVER_B_DIR.encode())
        server_b_files = sorted(json.loads(temp_socket.recv(MAX_BYTES_SIZE)),
                key=lambda f: f[0])
        temp_socket.close()
        server_a_files = sorted(get_list(SERVER_A_DIR),
                key=lambda f: f[0])
        #files = [*server_a_files, *server_b_files]
        #files.sort()
        fs_a = [f[0] for f in server_a_files]
        fs_b = [f[0] for f in server_b_files]
        if fs_a == fs_b: # Check files list of both servers
            print("READY - All dirs synced!")
            csocket.send(json.dumps(server_a_files).encode())
            client_socket.close()
            print(f"SUCCESS  Data has been sent to client {client_ip}:{client_port}")
        else:
            print("SERVER A:")
            pprint(server_a_files)
            print("SERVER B:")
            pprint(server_b_files)
            print("!" * 10, " ERROR - Something went wrong ", "!" * 10)

def init_handshake():
    """Initial sync of files in both dirs"""
    print("=" * 10, " INIT HANDSHAKE ", "=" * 10)

    # INITIAL HANSHAKE
    for [file, _, _] in get_list(SERVER_A_DIR):
        source = os.path.join(SERVER_A_DIR, file)
        destination = os.path.join(SERVER_B_DIR, file)
        cpf(source, destination)
    print(":DONE")


# WATCHDOG - REFERENCE:
# https://xiaoouwang.medium.com/create-a-watchdog-in-python-to-look-for-filesystem-changes-aaabefd14de4

#################################
#### SPECIFIC EVENT HANDLERS ####
#################################

def handle_create_event(event):
    """Handles CREATE EVENT under <path>"""
    fname = event.src_path.split("/")[-1]
    if os.path.isdir(event.src_path) or fname[0] == ".":
        return None
    destination = os.path.join(SERVER_B_DIR, fname)
    cpf(event.src_path, destination)
    print(f"[+] {fname} has been created - synced with <server_b>")

def handle_delete_event(event):
    """Handles DELETE EVENT under <path>"""
    fname = event.src_path.split("/")[-1]
    if os.path.isdir(event.src_path) or fname[0] == ".":
        return None
    remote_file = os.path.join(SERVER_B_DIR, fname)
    try:
        rmf(remote_file)
    except FileNotFoundError:
        pass
    print(f"[-] {fname} has been deleted - synced with <server_b>")

def handle_modify_event(event):
    """Handles MODIFY EVENT under <path>"""
    fname = event.src_path.split("/")[-1]
    if os.path.isdir(event.src_path) or fname[0] == ".":
        return None
    destination = os.path.join(SERVER_B_DIR, fname)
    if os.path.exists(destination):
        with open(event.src_path) as f1, open(destination) as f2:
            sbuff1 = f1.read()
            sbuff2 = f2.read()
            if sbuff1 != sbuff2: 
                cpf(event.src_path, destination)
                print(f"+++ {fname} has been modified - synced with <server_b>")
    else:
        handle_create_event(event)

if __name__ == "__main__":
    # INIT HANDSHAKE BETWEEN SERVER A & SERVER B
    init_handshake()

    # Init and event handler - watchdog
    event_handler = FileSystemEventHandler()

    # Configure CREATE, DELETE, MODIFY events
    # with main watchdog-event_handler
    event_handler.on_created  = handle_create_event
    event_handler.on_deleted  = handle_delete_event
    event_handler.on_modified = handle_modify_event

    # Init and schedule an observer
    fs_observer = Observer()
    fs_observer.schedule(event_handler=event_handler,
            path=SERVER_A_DIR,
            recursive=True)

    # Init a socket connection and observer
    server_socket = SERVER()
    fs_observer.start()
    try:
        while True:
            client_socket, (cip, cport) = server_socket.socket.accept()
            print(f"INFO    Got a Request from Client {cip}:{cport}")
            thread = threading.Thread(
                target=server_socket.process_request,
                args=[client_socket, cip, cport])
            thread.start()
    except Exception as ex:
        # Stop observer
        print(f"[Error]: {ex}")
        fs_observer.stop()
    fs_observer.join()
