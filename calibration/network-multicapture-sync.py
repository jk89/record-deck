# read args
# 1st 8132 [port]

import socket
import sys
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

len_argv = len(sys.argv)

if len_argv == 2:
    network_sync_port = sys.argv[1]
    UDP_PORT = int(network_sync_port)
    print((network_sync_port))
else:
    print(str(len_argv - 1) + " arguments provided. Expected 1 [port]")
    quit()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((UDP_IP, UDP_PORT))

lastTimeDevice0 = 0
lastTimeDevice1 = 0

import json
while True:
    message, address = server_socket.recvfrom(1024)
    data =json.loads(message)
    if (data["deviceId"] == 0):
        lastTimeDevice0 = data["time"]
    elif (data["deviceId"] == 1):
        lastTimeDevice1 = data["time"]
    print(lastTimeDevice0 - lastTimeDevice1, data)
