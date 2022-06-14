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
    - Modify zero_crossing_adc.ino and set the PWM_FREQUENCY to something that Ardiuno IDE Monitor or Serial Plot can handle, e.g. 1000 HZ
    - Flash zero_crossing_adc.ino onto your teensy 4.0.
    - Test collect data using Ardiuno IDE Monitor or Serial Plot
        - Format is "IGNORE, A, B, C, VN"
    - Rotate the motor such VN stays well above zero. Ensure that the channels are balanced and have similar voltage peaks.

# Collecting ADC data for calibration

    - Modify zero_crossing_adc.ino and set the PWM_FREQUENCY to full calibration logging speed e.g. 100kHz
    - Make sure zero_crossing_adc.ino has been loaded onto the Teensy 4.0
    - Remove old serial-data.dat temporary file
        - npm run serial:clean
    - Use a power drill to spin the motor at constant motion
    - Collect 1 second of serial data
        - npm run serial:collect_1s
    - Copy the temporary file /tmp/serial-data.dat to {Project_Directory}/datasets/data/calibration-data/serial-data.dat
    - Clean up the start and end of the file and make sure that for each line the columns are of the same size (same number of tabs), remove lines if nessesary.
    - Inspect the serial-data.dat file using the command and tune the kalman settings at the top (trial and error if nessesary, looking for kalman closely following the signal without to much noise)
        - npm run inspect:zero-crossing --dataset=serial-data.dat
    - When you are happy with the quality of the kalman data you can proceed to detecting the zero crossing

[Good ADC capture with Kalman filtering example output](zero-crossing-2-results.pdf)



