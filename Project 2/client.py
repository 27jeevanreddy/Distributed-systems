//Name: JEEVAN REDDY BODAPATLA
//ID:1001949287


#!/usr/bin/env python3
"""
    client socket implementation which
        client will send a request to SERVER A
        client will Recv files list from SERVER A
        client will print files data on output
"""
# To create and manipulate sockets
import socket

# To Serialize and Deserialize Objects
import json

# To handle SIGINT and exit
from signal import signal, SIGINT
from sys import exit

SERVER_A_IP = socket.gethostbyname(socket.gethostname())
SERVER_A_PORT = 55555
MAX_BYTES_SIZE = 2048

# SHELL INFO
print("CLIENT-SHELL")
print("------------")
print("\tSERVER IP   :", SERVER_A_IP)
print("\tSERVER PORT :", SERVER_A_PORT)
print("=" * 50 + "\n\n")

# INSTRUCTIONS
print("INSTRUCTIONS")
print("------------")
print("\tPress any key to show file list")
print("\tPress Ctrl-C to exit")

def kill_session(captured, _):
    print("\n" + "=" * 20, " END OF SESSION ", "=" * 20)
    print(":EXIT SUCCESS")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, kill_session)
    while True:
        _ = input(f"{SERVER_A_IP}> ")
        client_socket = socket.socket()
        client_socket.connect((SERVER_A_IP, SERVER_A_PORT))
        files = json.loads(client_socket.recv(MAX_BYTES_SIZE))
        LENGTH = 0
        for item in files:
            for attr in item:
                if len(attr) > LENGTH:
                    LENGTH = len(attr)
        for name, size, mtime in files:
            print(f"{name:<{LENGTH}} {size:^{LENGTH}} {mtime:^{LENGTH}}")
    
        client_socket.close()
