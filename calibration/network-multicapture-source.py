# read args
# 1st /dev/ttyACMP0 [tty teensy source]
# 2nd /tmp/serial-data.dat [stdout redirect (capture file storage)]
# 3rd 10.0.0.3 [host]
# 4th 8132 [port]

import sys
import socket
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

def send_obj(obj):
    str_obj = json.dumps(obj)
    sock.sendto(str_obj.encode(), (UDP_IP, UDP_PORT))

len_argv = len(sys.argv)

if len_argv == 5:
    source = sys.argv[1]
    std_redirect = sys.argv[2]
    network_sync_host = sys.argv[3]
    network_sync_port = sys.argv[4]

    UDP_IP = network_sync_host
    UDP_PORT = network_sync_port
    # print((source, std_redirect, network_sync_host, network_sync_port))
else:
    print(str(len_argv - 1) + " arguments provided. Expected 4 [tty source, stdout redirect, host, port]")
    quit()

    
