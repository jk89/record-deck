const process = require('process');
const fs = require('fs');
const readline = require('readline');

function process_args() {
    if (process.argv.length !== 3) {
        console.error("Expected 1 argument: [folder_name(e.g. run1)]");
        process.exit(1);
    }
    let [folder_name] = process.argv.slice(2, 3);
    path = `datasets/data/calibration-data/` + folder_name;

    return { path };
}

const args = process_args();
console.log(args);

const capture_device1_path = args.path + "/serial-data-device-1.jsonl";
const capture_device0_path = args.path + "/serial-data-device-0.jsonl";
const outfile_path = args.path + "/serial-combined.jsonl";

async function processLineByLine(file_path, device_id) {
    const fileStream = fs.createReadStream(file_path);
  
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    const lines = [];
  
    for await (const line of rl) {
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
        console.error(line, device_line_split_length);
        // process.exit(1);
      }

      
      // console.log(`Line from file: ${line}`, parsed_line, device_line_split.length);
    }
    return lines;
  }

async function main() {
   const device_0_lines = await processLineByLine(capture_device0_path, 0);
   const device_1_lines = await processLineByLine(capture_device1_path, 1);
   const combined_lines = device_0_lines.concat(device_1_lines);
   fs.writeFileSync(outfile_path, combined_lines.join("\n"));
   return combined_lines;
}

main().then(console.log).catch(console.error);


