# read args
# 1st /dev/ttyACMP0 [tty teensy source]
# 2nd /tmp/serial-data.dat [stdout redirect (capture file storage)]
# 3rd 10.0.0.3 [host]
# 4th 8132 [port]
# 5th 0/1 [device source id 0 or zero depending if running on Teensy 4.0 x1 or x2]

import sys
import socket
import json
import serial

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


def send_start_cmd_teensy(ser):
    binaryString = bytes([0,1])
    ser.write(binaryString)

def send_obj(obj):
    str_obj = json.dumps(obj)
    sock.sendto(str_obj.encode(), (UDP_IP, UDP_PORT))

len_argv = len(sys.argv)

SOURCE = None
STD_REDIRECT = None
NETWORK_SYNC_HOST = None
NETWORK_SYNC_PORT = None
SOURCE_DEVICE_ID = None

if len_argv == 6:
    source = sys.argv[1]
    SOURCE = source
    std_redirect = sys.argv[2]
    STD_REDIRECT = std_redirect
    network_sync_host = sys.argv[3]
    NETWORK_SYNC_HOST = network_sync_host
    network_sync_port = sys.argv[4]
    NETWORK_SYNC_PORT = network_sync_port

    UDP_IP = network_sync_host
    UDP_PORT = int(network_sync_port)
    source_device_id = int(sys.argv[5])
    SOURCE_DEVICE_ID = source_device_id
    # print((source, std_redirect, network_sync_host, network_sync_port, source_device_id))
else:
    print(str(len_argv - 1) + " arguments provided. Expected 5 [tty source, stdout redirect, host, port, source device id]")
    quit()

# open file for writing
file_object = open(STD_REDIRECT, 'a')
def append_line_to_std_redirect(line):
    file_object.write(line)
    pass

print("starting routine")

with serial.Serial(SOURCE) as ser: # , 19200, timeout=1
    while True:    
        # print("decode line")
        line = str(ser.readline().decode('utf-8'))
        # print("line", line)
        if (line == "waiting\r\n"):
            send_start_cmd_teensy(ser)
            continue
        line_split = line.split("\t")
        # print("line_split", line_split)
        time =int(line_split[0]) # time
        send_obj({"time": time, "deviceId": SOURCE_DEVICE_ID, "line": line})
        append_line_to_std_redirect(line)
# send start byte
# read serial
# write socket

# Close the file
file_object.close()

