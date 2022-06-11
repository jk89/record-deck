# record-deck project description

Smooth BLDC with a positional encoder, via a constant jerk model with input smoothing via a kalman filter, suitable for low to high (28k) rpm applications

## Directory layout

- /[control](control/README.md)
    - Motor control library (esc)
    - PID library
    - Inputs
        - PS4
- /[datasets](datasets/README.md)
    - scripts for downloading and processing datasets
    - /data
        folder to contain datasets
- /[calibration](calibration/README.md)
    - Tools for creating an angular zero-cross calibration map
    - Tools for collecting angular zero-cross measurements
- /[tracking](tracking/README.md)
    - Resources needed to create a kalman filter with a jerk model
- /design
    - mechanical
        - details of motor mechanical design
    - [electrical](./design/electrical/README.md)
        - details of esc circuit design

# Resources

## [Getting started](GETTING-STARTED.md)
## [Work logbook](resources/log.pdf)
## [Useful links](USEFUL-LINKS.md)

# Authors:
- Steve Kelsey
- Jonathan Kelsey


