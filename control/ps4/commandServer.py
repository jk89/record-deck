# Copyright Jonathan Kelsey 2021
# i listen on port 5000 and send commands to the ard

myIp = "127.0.0.1"
myPort = 5000

import socket
import json
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((myIp, myPort))
import struct
import math

import serial
ser = serial.Serial('/dev/ttyACM0')  # open serial port

def print_n_byte(target, n):
    return ((target&(0xFF<<(8*n)))>>(8*n)) # hex

axisMaxValue = 32767
def normaliseProfile(roll, pitch, thrust):
    global axisMaxValue
    # normalise between -1 to 1 on
    normRoll = roll / axisMaxValue
    normPitch = pitch / axisMaxValue
    # project inside a unit circle using elipse formula
    normRollAuthorityAdjusted = normRoll * math.sqrt(1 - ((normPitch * normPitch)/2)) 
    normPitchAuthorityAdjusted = normPitch * math.sqrt(1 - ((normRoll * normRoll)/2))
    return (normRollAuthorityAdjusted, normPitchAuthorityAdjusted, thrust)

def createArdByteString(roll, pitch, thrust):
    binaryString = bytes([thrust])
    binaryString = binaryString + struct.pack("<ff", roll, pitch)
    return binaryString 

nullProfile = createArdByteString(0, 0, 0)

nullProfileSentLast = False
def performStateChange(stateChange):
    global nullProfileSentLast
    if stateChange["type"] == "axes":
        value = stateChange["value"]
        #create binary profile
        (roll, pitch, thrust) = normaliseProfile(value["ljx"], value["ljy"], value["rt"])
        profile = createArdByteString(pitch, roll, thrust)
        #profile = bytearray([print_n_byte(value["ljx"], 0), print_n_byte(value["ljx"], 1), print_n_byte(value["ljy"], 0), print_n_byte(value["ljy"], 1), ((value["rt"]))])
        if thrust == 0:
            return
        if thrust < 20:
            profile = createArdByteString(roll, pitch, 20)
        ser.write(profile)
        print(("profile", profile, len(profile)))
    else:
        if stateChange["value"] == "x":
            if (nullProfileSentLast == False):
                ser.write(nullProfile)
                print(("profile", nullProfile))
                nullProfileSentLast = True
        elif stateChange["value"] == "t":
            startProfile = createArdByteString(0, 0, 20)
            ser.write(startProfile)
            print(("profile", startProfile))
            nullProfileSentLast = False
        
    print(stateChange)

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    jsonProfile = json.loads(data)
    performStateChange(jsonProfile)