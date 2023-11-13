const process = require('process');
const { SerialPort, ReadlineParser } = require('serialport');
const fs = require("fs");
const net = require("net");
const { PromiseSocket } = require("promise-socket");

/**
 * A function to process this programs cli arguments and throws meaningful errors if validation fails. 
 * @return {{device_id: number, source: string, host: string, port: number}}
 *  Returns a arguments object, with members: 
 *    - device_id [number], identifier for the logging device, 0 indicates adc measurement device and 1 indicates the encoder measurement device.
 *    - source [string], source of the logging data, e.g. normally Teensy can be found at '/dev/ttyACMP0'
 *    - host [string], ip address of the host where this program will send Teensy data to, e.g. '192.168.0.26'
 *    - port [number], port of the host where we will send the data on, e.g. 8132
 */
function process_args() {
    // validate number of arguments
    if (process.argv.length !== 7) {
        console.error("Expected 4 arguments: [source (e.g. '/dev/ttyACMP0'), network_sync_host (e.g. '192.168.0.26'), network_sync_port (e.g. 8132), seconds_to_collect (e.g. 1)]");
        process.exit(1);
    }

    // unpack expected number of arguments
    let [device_id, source, host, port, seconds_to_collect] = process.argv.slice(2, 7);

    // try and parse device id as int
    const device_id_int = parseInt(device_id);
    if (isNaN(device_id_int)) {
        console.error("Could not parse provided device_id to a number: ", device_id);
        process.exit(1);
    }
    else {
        device_id = device_id_int;
    }

    // try and parse port as int
    const port_int = parseInt(port);
    if (isNaN(port_int)) {
        console.error("Could not parse provided port to a number: ", port);
        process.exit(1);
    }
    else {
        port = port_int;
    }

    // try and parse seconds_to_collect as int
    const seconds_to_collect_int = parseInt(seconds_to_collect);
    if (isNaN(seconds_to_collect_int)) {
        console.error("Could not parse provided seconds_to_collect_int to a number: ", seconds_to_collect);
        process.exit(1);
    }
    else {
        seconds_to_collect = seconds_to_collect_int;
    }

    // return args object
    return { device_id, source, host, port, seconds_to_collect };
}

const plaid_speed = 5000000;
/**
 * A function to retrieve a serial port instance for the Teensy.
 * @param {string} source Source of the logging data, e.g. normally Teensy can be found at '/dev/ttyACMP0'.
 * @returns {SerialPort}
 * Returns a SerialPort object from which we can retrieve Teensy data.
 */
function get_teensy_serial_port(source) {
    return new SerialPort(
        {
            path: source,
            baudRate: plaid_speed
        }
    );
}

/**
 * A function to open a connection to a host, write all provided string data to the host and finally terminate the socket connection.
 * @param {string} host ip address of the host where this program will send Teensy data to, e.g. '192.168.0.26'.
 * @param {number} port port of the host where we will send the data on, e.g. 8132.
 * @param {string} data_str the data string to be written to the host.
 */
async function transmit_data(host, port, data_str) {
    const socket = new net.Socket();
    const promise_socket = new PromiseSocket(socket);
    await promise_socket.connect({ port, host });
    console.log("Connected to host");
    await promise_socket.writeAll(data_str);
    console.log("Wrote data to host");
    await promise_socket.end();
    console.log("Terminated connection to host");
}

// Process cli program arguments
const args = process_args();

// Define global to hold all recieved data from Teensy.
/** @type {Array.<{line: string, deviceId: number, time: number}>} */
const file_data = [];

/**
 * Function to remove previous data collected tmp file, to bind to the Teensy serial port and recieves, parses and caches data from it.
 * @param {string} source source of the logging data, e.g. normally Teensy can be found at '/dev/ttyACMP0'.
 * @param {number} device_id identifier for the logging device, 0 indicates adc measurement device and 1 indicates the encoder measurement device.
 */

const newline = `
`;
function main(source, device_id) {
    const teensy_serial_port = get_teensy_serial_port(source);
    const parser = teensy_serial_port.pipe(new ReadlineParser({ delimiter: '\n' }));

    fs.rmSync(`/tmp/serial-data-device-${device_id}.dat`, {
        force: true,
    });

    parser.on("data", (line) => {
        if (device_id == 1 || device_id == 0) {
            // check if we have a terminating "END/n" message
            // line
            /*if (line["0"] === "E" && line["1"] === "N" && line["2"] === "D" && line.charCodeAt(3) == 13) {
                console.log("Got end signal from ADC teensy");
                // we have a termination signal
                return shutdown(args);
            }*/

            const line_split = line.split("\t");
            const time = parseInt(line_split[0]);
            // if time is a valid field
            if (!isNaN(time) && time != null) {
                const network_obj = { "time": time, "deviceId": device_id, line: line };
                file_data.push(network_obj);
            }
        }
        else {
            throw "Device_id can be 1 or 0";
        }
    });

    // when the teensy is unplugged run the shutdown procedure.
    teensy_serial_port.on("close", async () => {
        await shutdown(args);
    });

    // wait a little for teensy to start
    setTimeout(() => {
        const msg = Buffer.from([args.seconds_to_collect]);
        console.log("writing a message", msg);
        teensy_serial_port.write(msg);
        // if adc device 1 shutdown after 1.5 * args.seconds_to_collect
        if (device_id === 0) {
            setTimeout(()=>{
                return shutdown(args);
            },args.seconds_to_collect * 1500);
        }
    }, 1000);

    // teensy_serial_port.write("Far Out in the uncharted backwaters of the unfashionable end of the Western Spiral arm of the galaxy lies a small unregarded yellow sun.");
}

// invoke main
main(args.source, args.device_id);

let debounce = 0;
/**
 * Function to save the retrieved file_data type into a jsonl file, and to finally attempt to transmit it to a
 * running network-multicapture-sync host.
 * @param {{device_id: number, source: string, host: string, port: string}} args 
 */
async function shutdown(args) {
    debounce++;
    // prevent multiple Ctrl-c signals from triggering the core shutdown logic.
    if (debounce <= 1) {
        const out_data_location = `/tmp/serial-data-device-${args.device_id}.jsonl`;

        console.log(`The server is shutting down.`);
        console.log("Please wait why we flush received data to disk...");

        try {
            const file_str = file_data.map((line_data) => {
                return JSON.stringify(line_data);
            }).join("\n");

            // save file_data
            fs.writeFileSync(out_data_location, file_str);
            console.log("Wrote data to file: ", out_data_location);

            // transmit file_data to network-multicapture-sync host
            await transmit_data(args.host, args.port, JSON.stringify(file_data));
            console.log("Transmitted data to host");
            console.log("Shutdown complete ✅");

            process.exit(0);
        }
        catch (err) {
            console.log("Flush or transmit failed... shutting down anyway ❌");
            console.error(err, err.stack);
            process.exit(0);
        }

    }
    
}

// bind shutdown to Ctrl-c signal
process.on('SIGINT', async () => {
    await shutdown(args);
});