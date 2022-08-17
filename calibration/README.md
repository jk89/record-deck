# Galvanically isolated ADC/Encoder circuit

![circuit](../resources/galvanically-isolated-adc-encoder-circuit.png)


# Connecting to JK-SBDLC-SMT-REV2. 

## ADC/ADC-ETC information table:

| PHASE       | A   | B      | VN    | C     |
|-------------|-----|--------|-------|-------|
| Teensy 4.0 #1 pin         | 14  | 15     | 17    | 16    |
| COLOUR      | RED | YELLOW | GREEN | BLACK |
| TRIG        | 0   | 1      | 2     | 3     |
| DONE        | 0   | 1      | 0     | 1     |
| HW-CH       | 1   | 2      | 3     | 4     |
| ADC-CH      | 7   | 8      | 11    | 12    |

## Other pins

- Connect Teensy 4.0 #1 ground to pin 7 of JK-SBDLC-SMT-REV2.

# Connecting to AS5147.

# Encoder information table:

AS5147 pin| 5v| 3.3v| x| csn| clk| mosi| miso| GND
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Teensy 4.0 #2 pin| 3.3v| 3.3v| x| 10| 22| 11| 12| GND

# Connecting Teensy 4.0 #1 with Teensy 4.0 #2 with two H11L1 optocouplers.

Teensy 4.0 #1 acts as a master and sends signals via two galvanically isolated optocouplers to Teensy 4.0 #2. 

# Connection information table:

H11L1 #1 RESET pin| 1 (ANODE)| 2 (CATHODE)| 3(NC)| 4(Vo)| 5 (GND)| 6(VCC)
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Teensy 4.0 #1 pin| 3| GND| X| X| X| X
Teensy 4.0 #2 pin| X| X| X| 3| GND| 3.3V

H11L1 #2 CLK pin| 1 (ANODE)| 2 (CATHODE)| 3(NC)| 4(Vo)| 5 (GND)| 6(VCC)
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Teensy 4.0 #1 pin| 8| GND| X| X| X| X
Teensy 4.0 #2 pin| X| X| X| 7| GND| 3.3V

# Collecting ADC/Encoder data for calibration

Need two computers to collect clean data from this setup. One needs to be a laptop which is disconnected from everything, networking via wifi nessesary.

- Modify zero_crossing_adc.ino and set the PWM_FREQUENCY to full calibration logging speed e.g. 100kHz.
- Make sure zero_crossing_adc.ino has been loaded onto the Teensy 4.0 #1.
- Make sure zero_crossing_encoder_slave.ino has been loaded onto the Teensy 4.0 #2.
- Find network address of computer #2 by running `ifconfig` or similar. e.g. '192.168.0.26'.
- Plug Teensy 4.0 #2 (Encoder) into computer #2.
- Plug Teensy 4.0 #1 (ADC) into computer #1 (needs to be a fully charged laptop disconnected from everything else apart from the Teensy [not ethernet allowed]).
- Start the network sync program on computer #2. `npm run network-serial:collect-sync > network-data.dat`. Redirect the output to a file.
- Start the network source program on computer #2. `npm run network-serial:collect-source --device_id=1 --sync_host=192.168.0.26`.
- Use a power drill to spin the motor at constant motion, Rotate the motor such VN stays well above zero. Ensure that the channels are balanced and have similar voltage peaks.
- Start data collection by running the network source program on computer #1, `npm run network-serial:collect-source --device_id=0 --sync_host=192.168.0.26`.
- After you are happy enough data has been collected stop collection by unplugging Teensy 4.0 #1.
- Stop `network-serial:collect-source` for both computers.
- Take the `serial-data-device-x.jsonl` file from the /tmp folder's from each computer and place into a folder under `./datasets/data/calibration-data/[experiment-name]/`
- Combine datasets into a single file `node calibration/combine-multicapture-files.js [experiment-name]`
- Rename the resultant file the same name as the experiment name and move to parent folder.
- Process the collected 'network-data.dat' `npm run combine:rotation-voltage-network-data --dataset=network-dat-3.dat`, you will recieve a file 'calibration-data.dat' if the successful.
- Inspect the 'calibration-data.dat' file using the command and tune the kalman settings at the top (trial and error if nessesary, looking for kalman closely following the signal without to much noise).
    - `npm run inspect:rotation-voltage-data --dataset=calibration-data.dat`
- When you are happy with the quality of the kalman data you can proceed to detecting the zero crossing.
    - `npm run smooth:rotation-voltage-data --dataset=calibration-data.dat`
- Next take the smoothed network data and attempt to cluster it `npm run detect:zero-crossing`.


  803  node calibration/combine-multicapture-files.js testinf3
  804  cp datasets/data/calibration-data/testinif/serial-combined.jsonl datasets/data/calibration-data/testinif3.jsonl
  805  cp datasets/data/calibration-data/testinf3/serial-combined.jsonl datasets/data/calibration-data/testinif3.jsonl
  806  npm run combine:rotation-voltage-network-data --dataset=testinif3.jsonl

[Good ADC capture with Kalman filtering example output of inspect:rotation-voltage-data](inspect-zero-crossing-results.pdf)

# JK-SBDLC-SMT-REV2

- [Electrical design](../design/electrical)

# H11L1 Opto-isolator

- [Datasheet](https://www.mouser.com/datasheet/2/149/H11L1M-1010369.pdf)

# AS5147P Encoder

- [Datasheet](https://ams.com/documents/20143/36005/AS5147P_DS000328_2-00.pdf)
