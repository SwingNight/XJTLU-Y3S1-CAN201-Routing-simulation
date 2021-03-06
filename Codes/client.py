import json
import os
import sys
import threading
import time
from socket import *
from server import server_connect


client = socket(AF_INET, SOCK_DGRAM)


def get_path():
    realpath = os.path.realpath(sys.argv[0]).split("/")
    path = ""
    for i in range(1, len(realpath) - 1):
        path = path + "/" + realpath[i]
    return path


def read(path):
    f = open(path, "rb")
    content = json.load(f)
    f.close()
    return content


def write(path, content):
    f = open(path, "w")
    f.write(json.dumps(content))
    f.close()


def temp_client(node, root):
    distance = {}
    path = root + "/" + node + "_distance.json"
    distance[node] = read(path)
    print("Distance: ", distance)
    path = root + "/" + node + "_client.json"
    write(path, distance)


def client_connect(node, root, key, ip):
    try:
        client.sendto(node.encode(), ip)  # ip: [server_name, server_port]
        client.recvfrom(1024)  # node
        path = root + "/" + node + "_client.json"
        f = open(path, "rb")
        size = os.path.getsize(path)
        message = str(size).encode()
        client.sendto(message, ip)
        client.recvfrom(1024)  # size
        for line in f:
            client.sendto(line, ip)  # sends file to client
        f.close()
        client.recvfrom(1024)  # file
        client.close()
        print("Client: successfully send distance to ", key)
    except:
        client.close()


def connection(node, root):
    path = root + "/" + node + "_ip.json"
    ip = read(path)
    del ip[node]  # Delete my ip
    print("Other ip: ", ip)
    time.sleep(5)
    for key, value in ip.items():  # key = node, value[0] = ip, value[1] = port
        value = (value[0], value[1])
        client_connect(node, root, key, value)
    time.sleep(10)


def traverse(root):
    root_list = []
    temp = os.listdir(root)
    for i in temp:
        root_list.append(i)
    return root_list


def collect_distance(node, root):
    other_temp = []
    path = root + "/" + node + "_client.json"
    my_temp = read(path)
    for i in traverse(root):
        if "_server.json" in i:  # Server: received distance from other nodes
            if not node + "_server.json" in i:
                other_temp.append(i)

    for i in other_temp:
        path = root + "/" + i
        distance = read(path)
        print("Content:", distance)
        for key in distance.keys():
            if key in my_temp:
                pass
            else:
                my_temp[key] = distance[key]
    print("Collect distance ", my_temp)
    path = root + "/" + node + "_client.json"
    write(path, my_temp)


def bellman_ford(node, root):
    edges = []
    vertices = ''
    path = root + "/" + node + "_client.json"
    distance = read(path)
    for key in distance.keys():
        for i in distance[key]:
            edges.append([key, i, distance[key][i]])
        vertices = vertices + key

    temp = {v: sys.maxsize for v in vertices}  # distance dictionary
    temp[node] = 0
    before = {v: None for v in vertices}
    # traverse n-1 times
    for i in range(len(vertices) - 1):
        for edge in edges:  # relax edges
            if temp[edge[0]] + edge[2] < temp[edge[1]]:
                temp[edge[1]] = temp[edge[0]] + edge[2]
                before[edge[1]] = edge[0]
    # find shortest hop
    output = {}
    hop = []
    for i in vertices:
        if i != node:
            pre = before[i]
            hop.append(i)
            while pre != None:
                hop.append(pre)
                pre = before[pre]
            hop.reverse()
            output[i] = {"distance": temp[i], "next_hop": hop[1]}
    path = root + "/" + node + "_output.json"
    write(path, output)
    print("########################################################")
    print("Output:", output)


def delete(root):
    delete_list = []
    for i in traverse(root):
        if "_client" in i:
            delete_list.append(i)
        elif "_server" in i:
            delete_list.append(i)
    print("Delete: ", delete_list)

    for i in delete_list:
        path = root + "/" + i
        os.remove(path)
    print("Deleted")


def process(node, root):
    temp_client(node, root)
    while True:
        connection(node, root)
        collect_distance(node, root)
        bellman_ford(node, root)
        time.sleep(30)
        delete(root)
        sys.exit(0)


def run_client(node):
    print("Node ", node)
    root = get_path()
    thread = threading.Thread(target=server_connect, args=(node, root))
    thread.start()
    process(node, root)
