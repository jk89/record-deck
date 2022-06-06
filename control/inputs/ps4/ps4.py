#!/usr/bin/python

# Copyright Jonathan Kelsey 2021

import os, sys
import subprocess
import datetime

buttonMap = {
    "x": {"type": "button", "index": 0},
    "s": {"type": "button", "index": 3},
    "c": {"type": "button", "index": 1},
    "t": {"type": "button", "index": 2},
    "l": {"type": "axis", "index": 6, "valueWhenUp": -32767},
    "r": {"type": "axis", "index": 6, "valueWhenUp": 32767},
    "u": {"type": "axis", "index": 7, "valueWhenUp": -32767},
    "d": {"type": "axis", "index": 7, "valueWhenUp": 32767},
    "ls": {"type": "button", "index": 4},
    "rs": {"type": "button", "index": 5},
    "ljc": {"type": "button", "index": 11},
    "rjc": {"type": "button", "index": 12},
}
axisMap = {
    "ljx": {"type": "axis", "index": 0, "minValue": -32767, "maxValue": 32767}, # LEFT TO RIGHT
    "ljy": {"type": "axis", "index": 1, "minValue": 32767, "maxValue": -32767}, # DOWN TO UP
    "rjx": {"type": "axis", "index": 3, "minValue": -32767, "maxValue": 32767}, # LEFT TO RIGHT
    "rjy": {"type": "axis", "index": 4, "minValue": 32767, "maxValue": -32767}, # DOWN TO UP
    "lt": {"type": "axis", "index": 2, "minValue": -32767, "maxValue": 32767}, # RELEASED TO PRESSED
    "rt": {"type": "axis", "index": 5, "minValue": -32767, "maxValue": 32767}, # RELEASED TO PRESSED
}

watchConfig = {
    "buttons": ["x", "t"],
    "axes": {
        "ljx": {},
        "ljy": {},
        "rt": {"minValue": 0, "maxValue": 255}
    }
}

def lineDataCleaner(lineData):
    outData = []
    for i in lineData:
        sectionSplit = i.split(" ")
        for j in sectionSplit:
            if j.isalnum():
                outData.append(j)
    return outData

def buttonDataClearer(input):
    out = []
    for i in input:
        for j in i:
            if j.isalnum() or j.lstrip('-').isalnum():
                out.append(j)
    return out

def accumulator(input):
    output = {}
    for i in range(int(len(input) / 2)):
        j = i * 2
        k = j + 1
        key = input[j]
        value = input[k]
        output[key] = value
    return output

def print_n_byte(target, n):
    return ((target&(0xFF<<(8*n)))>>(8*n)) # hex

# So the left arrow buttons are in the axis data
# lets mapthem out
# we will have an axis map and a button map

class PyPS4():
    def __init__(self, _cb=None, interface="/dev/input/js0", _buttonMap=buttonMap, _axisMap=axisMap, _watchConfig=watchConfig):
        self.oldButtonData = None
        self.oldAxisData = None
        self.axisState = {}
        self.interface = interface
        self.buttonMap = _buttonMap
        self.axisMap = _axisMap
        self.watchConfig = watchConfig
        self.cb = _cb
        self.axisState
        for neededAxis in self.watchConfig["axes"].keys():
            self.axisState[neededAxis] = 0
        self.proc = subprocess.Popen("jstest /dev/input/js0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


    def event(self, data):
         #["button",data["value"]]
        #print("in event", data)
        if (data["type"]=="axes"):
            for axisKeyChanged in data["value"].keys():
                self.axisState[axisKeyChanged] = data["value"][axisKeyChanged]
        #    #print(self.axisState)
        #    arrayData2 = [self.axisState["ljx"], self.axisState["ljy"], self.axisState["rt"]]##

        #    arrayData = [print_n_byte(self.axisState["ljx"], 0), print_n_byte(self.axisState["ljx"], 1), print_n_byte(self.axisState["ljy"], 0), print_n_byte(self.axisState["ljy"], 1), ((self.axisState["rt"]))]
        #    #print(bytearray(arrayData))
        #    byteArray = bytearray(arrayData)# bytearray([self.axisState["rt"]]) #
        #    print(arrayData2)
        #    print(byteArray)
        #    #print(''.join('{:02x}'.format(x) for x in byteArray))
        #    if self.cb is not None:
        #        self.cb(["axes",byteArray])
        #else:
        #    if self.cb is not None:
        #        self.cb(["button",data["value"]])
            #print(data)
        if self.cb is not None:
            self.cb(data, self.axisState)

    def processData(self, buttonData, axisData):
        #print("axisData", axisData)
        if self.oldButtonData is None:
            self.oldButtonData = buttonData
        if self.oldAxisData is None:
            self.oldAxisData = axisData

        buttonPressed = None
        for buttonKeyIdentifier in self.buttonMap.keys():
            # e.g. s,d,r,l,c,x
            keyMapDecodeInformation = self.buttonMap[buttonKeyIdentifier]
            if keyMapDecodeInformation["type"]=="button":
                index = str(keyMapDecodeInformation["index"])
                if (index in self.oldButtonData and index in buttonData) and (self.oldButtonData[index] == "off" and buttonData[index] == "on"):
                    buttonPressed = (buttonKeyIdentifier)
            elif keyMapDecodeInformation["type"]=="axis":
                index = str(keyMapDecodeInformation["index"])
                valueWhenUp = str(keyMapDecodeInformation["valueWhenUp"])
                if (index in self.oldButtonData and index in buttonData):
                    if self.oldAxisData[index]=="0" and axisData[index]==valueWhenUp:
                        buttonPressed = buttonKeyIdentifier
                        break

        axisChangeData={}
        for axisKeyIdentifier in self.axisMap.keys():
            axisMapDecodeInformation = self.axisMap[axisKeyIdentifier]
            index = str(axisMapDecodeInformation["index"])
            axisValue = int(axisData[index])
            if axisValue != int(self.oldAxisData[index]):
                axisChangeData[axisKeyIdentifier] = axisValue

        if self.watchConfig["buttons"] is not None:
            for buttonsNeeded in self.watchConfig["buttons"]:
                if (buttonPressed == buttonsNeeded):
                    self.event({"type":"button", "value": buttonPressed})

        trackData = {}
        for neededAxisKey in self.watchConfig["axes"].keys():
            #print("neededAxisKey", neededAxisKey)
            axisInfo = self.watchConfig["axes"][neededAxisKey]
            if (("minValue" in axisInfo or "maxValue" in axisInfo) and neededAxisKey in axisChangeData):
                #print("here")
                originalData = axisChangeData[neededAxisKey]
                originalScale = self.axisMap[neededAxisKey]
                oldMin = originalScale["minValue"]
                oldMax = originalScale["maxValue"]
                newMin = axisInfo["minValue"]
                newMax = axisInfo["maxValue"]
                newValue = int((((originalData - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin)
                trackData[neededAxisKey]=newValue
            elif neededAxisKey in axisChangeData:
                trackData[neededAxisKey]=axisChangeData[neededAxisKey]
                #print("there")
        #print("trackData", trackData)
        if (len(trackData.keys())>0):
            self.event({"type":"axes", "value": trackData})

        self.oldButtonData = buttonData # update previous state cache
        self.oldAxisData = axisData #
        


    def processLine(self, line):
        splitLines = line.split("Buttons:")
        if (len(splitLines) == 2):
            axesData = buttonDataClearer([i.split(" ") for i in splitLines[0].split("Axes: ")[1].split(":")])
            buttonData = lineDataCleaner(splitLines[1].split(":"))
            axesDataMap = accumulator(axesData)
            buttonDataMap = accumulator(buttonData)
            self.processData(buttonDataMap, axesDataMap)

    def start(self):
        while self.proc.poll() is None:
            line = self.proc.stdout.readline()
            self.processLine(line)



# pyps4 = PyPS4()
# pyps4.start()
