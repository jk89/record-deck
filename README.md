# record-deck project description

Smooth BLDC with a positional encoder, via a constant jerk model with input smoothing via a kalman filter, suitable for low to high (28k) rpm applications. Aspirationally suitable for driving a bespoke record deck AC motor.

## Directory layout

- /[control](control)
    - Physical model
    - Motor control library (esc)
    - PID library
    - Inputs
        - PS4
- /[datasets](datasets)
    - scripts for downloading and processing datasets
    - /data
        folder to contain datasets
- /[calibration](calibration)
    - Tools for creating an angular zero-cross calibration map
    - Tools for collecting angular zero-cross measurements
- /[tracking](tracking)
    - Resources needed to create a kalman filter with a jerk model
    - [absolute-rotation-encoder-AS5147P driver](tracking/absolute-rotation-encoder-AS5147P)
- /design
    - mechanical
        - details of motor mechanical design
    - [electrical](./design/electrical)
        - details of esc circuit design

# Resources

## [Getting started](GETTING-STARTED.md)
## [Work logbook 1](resources/log.pdf)
## [Work logbook 2](resources/log2.pdf)
## [Work logbook 3](resources/log3.pdf)
## [Work logbook 4](resources/log4.pdf)
## [Work logbook 5](resources/log5.pdf)
## [Work logbook 6](resources/log6.pdf)
## [Work logbook 7](resources/log7.pdf)
## [Useful links](USEFUL-LINKS.md)

# Publication information

Note this repository is un-released, and is not tested. Code is released as is. You run the risk of damaging hardware and injuring yourself when proceeding with this code.

# Credits:
- Mechanical CAD design and material science - Steve Kelsey
- EE design and software enginnering - Jonathan Kelsey
- Experimental assistant - Andres Soler
- [Circuit reference](https://simple-circuit.com/arduino-sensorless-bldc-motor-controller-esc/)