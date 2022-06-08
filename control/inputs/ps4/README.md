# Custom linux ps4 bldc motor controller library

## Dependancies

1. jstest is what i've used to decode input from a PS4 controller. I tried pyPS4Controller but could not get it to work so built a parser for jstest output
	- sudo apt-get install joystick
2. pyserial is a library for sending command via usb to the teensy 4.0
	- (sudo [for global usage]) pip3 install -r pip.freeze

## How to run

0. cd ./control/ps4
1. Start sending commands from ps4 controller to remote: python remoteCommand.py
2. Starting the teensy command server python commandServer.py
3. Open SerialPlot select ttyACM0 and click open. FIXME
4. Press triangle on the PS4 controller to startup.
5. Press square on the PS4 controller to stop.
6. Squeeze right trigger to control thrust setting (WARNING as this is not working currently you could burn out hardware by using the throttle )
