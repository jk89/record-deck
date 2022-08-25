const process = require('process');
const fs = require('fs');
const readline = require('readline');

/**
 * Processes this programs cli arguments and throws meaningful errors if validation fails. 
 * @return {{path: string}}
 *  Returns a arguments object, with members: 
 *    - path [string], the path to a calibration-data dataset folder containing two jsonl files one from Teensy #1 and one from Teensy #2
 */
function process_args() {
    if (process.argv.length !== 3) {
        console.error("Expected 1 argument: [folder_name(e.g. run1)]");
        process.exit(1);
    }
    let [folder_name] = process.argv.slice(2, 3);
    path = `datasets/data/calibration-data/` + folder_name;

    return { path };
}

/**
 * Loads a jsonl file into memory asynchronously given its file_path
 * @param {string} file_path 
 * @return {Promise<Array.<{line: string, deviceId: number, time: number}>>}
 * Returns a promise for a parsed list of json objects collected within a given input jsonl file. 
 *   - line [string], one raw line from a given device.
 *   - deviceId [string], identifier for the device. 0 has the adc data and 1 the encoder data.
 *   - time [number], the clock count from the device. At 90kHz you would expect time of 90,000 after one second data collection.
 */
async function process_line_by_line(file_path) {

    const fileStream = fs.createReadStream(file_path);
    const rli = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });
    const lines = [];
  
    for await (const line of rli) {
      const parsed_line = JSON.parse(line);
      const device_line = parsed_line.line;
      const device_line_split = device_line.split("\t");
      const device_line_split_length = device_line_split.length;

      if (parsed_line.deviceId == 0 && device_line_split_length == 5) {
        lines.push(line);
      }
      else if (parsed_line.deviceId == 1 && device_line_split_length == 2) {
        lines.push(line);
      }
      else {
        console.error(`Unexpected number of lines: ${device_line_split_length}, for this device ${parsed_line.deviceId}. Expected 5 or 2. Raw line:`, line);
      }
    }

    return lines;
  }

// Process cli program arguments
const args = process_args();
// Create file paths for the jsonl files, following the naming convention.
const capture_device1_path = args.path + "/serial-data-device-1.jsonl";
const capture_device0_path = args.path + "/serial-data-device-0.jsonl";
// Create a destination for the output of the combined jsonl file
const outfile_path = args.path + "/serial-combined.jsonl";

/**
 * Main loads both jsonl files into memory, concatenates them into a single list and then write them out to a new jsonl file, and then returns the concatenated list.
 * @return {Promise<Array.<{line: string, deviceId: number, time: number}>>}
  * Returns a promise for a parsed list of json objects collected within a given input jsonl file. 
 *   - line [string], one raw line from a given device.
 *   - deviceId [string], identifier for the device. 0 has the adc data and 1 the encoder data.
 *   - time [number], the clock count from the device. At 90kHz you would expect time of 90,000 after one second data collection.
  */
async function main() {
   const device_0_lines = await process_line_by_line(capture_device0_path, 0);
   const device_1_lines = await process_line_by_line(capture_device1_path, 1);
   const combined_lines = device_0_lines.concat(device_1_lines);
   fs.writeFileSync(outfile_path, combined_lines.join("\n"));
   return combined_lines;
}

// Executes main and then prints the combined lines list or console.errors any exception.
main().then(console.log).catch(console.error);


