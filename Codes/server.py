import json
from socket import *


server = socket(AF_INET, SOCK_DGRAM)


def set_server(node, root):
    path = root + "/" + node + "_ip.json"
    f = open(path, "rb")
    ip = json.load(f)
    f.close()
    my_port = ip[node]
    server_port = (my_port[0], my_port[1])  # server_port = my ip
    server.bind(server_port)


def server_connect(node, root):
    set_server(node, root)
    client = []
    while True:
        message, address = server.recvfrom(1024)
        if not client:
            node = message.decode()
            print("Server: receive from ", node)
            client = [node, address]
            server.sendto("node".encode(), address)  # node
        elif address == client[1]:
            node = client[0]
            receive_size = 0
            size = message.decode()
            file_size = int(size)
            server.sendto("size".encode(), address)  # size
            path = root + "/" + node + "_server.json"
            f = open(path, "wb")
            while receive_size < file_size:
                if file_size - receive_size > 1024:
                    buffer = 1024
                else:
                    buffer = file_size - receive_size  # The last packet
                data, address = server.recvfrom(buffer)
                receive_size = receive_size + len(data)
                f.write(data)
            else:
                f.close()
                server.sendto("file".encode(), address)  # file
                client = []
