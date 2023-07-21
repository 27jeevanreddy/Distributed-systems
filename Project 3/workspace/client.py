"""Name:Jeevan Reddy Bodapatla
   Id:1001949287
"""

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

from sys import argv, stderr, exit

SERVER_A_IP = socket.gethostbyname(socket.gethostname())
SERVER_A_PORT = 55555
MAX_BYTES_SIZE = 2048

def handle_error(message="Something went wrong with command parameters!"):
    """
    Handles any errors by prompting the message to [client]
    """
    print("[ERROR]:", message, file=stderr)
    print("[Usage]:", "python <client.py> -{lock | unlock} -{file index}", file=stderr)
    exit(1)

# Fetching of client command
if len(argv) == 3:
    command = " ".join(argv[1:])
    command = bytes(command.replace("-", ""), "utf-8")
elif len(argv) == 2:
    handle_error("Insufficient command parameters!")
elif len(argv) == 1:
    command = bytes("no locks", "utf-8")
else:
    handle_error("Unknown command parameters!")

# Connecting to server_a through a <client_socket>
if __name__ == "__main__":
    client_socket = socket.socket()
    client_socket.connect((SERVER_A_IP, SERVER_A_PORT))
    client_socket.send(command)
    files = json.loads(client_socket.recv(MAX_BYTES_SIZE))

    # Prompt the file list to <client>
    LENGTH = 0
    for item in files:
        for attr in item:
            if len(attr) > LENGTH:
                LENGTH = len(attr)
    i = 0
    for name, size, mtime in files:
        print(f"[{i}]\t{name:<{LENGTH}} {size:^{LENGTH}} {mtime:^{LENGTH}}")
        i += 1

    client_socket.close()
