# Install SerialPlot
    -  sudo apt install build-essential qtbase5-dev libqt5serialport5-dev libqt5svg5-dev cmake mercurial
    - hg clone https://hg.sr.ht/~hyozd/serialplot
    -  cd serialplot/
    - mkdir build && cd build
    - cmake ..
 	- make

# Configure SerialPlot
    - SerialPlot-Profile.ini is contained within ./serial_plot
    - In serialplot File->Load Settings.... find the ini file

# Connecting to JK-SBDLC-SMT-REV2. 

## ADC/ADC-ETC information table:

| PHASE       | A   | B      | VN    | C     |
|-------------|-----|--------|-------|-------|
| PIN         | 14  | 15     | 17    | 16    |
| COLOUR      | RED | YELLOW | GREEN | BLACK |
| TRIG        | 0   | 1      | 2     | 3     |
| DONE        | 0   | 1      | 0     | 1     |
| HW-CH       | 1   | 2      | 3     | 4     |
| ADC-CH      | 7   | 8      | 11    | 12    |

## Other pins

- Connect teensy ground to pin 7 of JK-SBDLC-SMT-REV2.

# Logging ADC data

    - Wire your teensy 4.0 to your JK-SBDLC-SMT-REV2.4 using the information above.
    - Flash zero_crossing_adc.ino onto your teensy 4.0.
    - Collect data using Ardiuno IDE or Serial Plot
        - Format is "A, B, C, VN"
    - Rotate the motor such VN stays well above zero.

[Example output](https://github.com/jk89/record-deck/blob/FEATURES/tracking/calibration/zero_crossing_adc/adc-example-12bit-output.csv)
