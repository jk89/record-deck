const dgram = require('dgram');
const process = require('process');
const { SerialPort, ReadlineParser } = require('serialport');
const fs = require('fs/promises');

function process_args() {
    if (process.argv.length !== 6) {
        console.error("Expected 3 arguments: [source (e.g. '/dev/ttyACMP0'), network_sync_host (e.g. '192.168.0.26'), network_sync_port (e.g. 8132)]");
        process.exit(1);
    }
    let [device_id, source, host, port] = process.argv.slice(2, 6);

    const device_id_int = parseInt(device_id);
    if (isNaN(device_id_int)) {
        console.error("Could not parse provided device_id to a number: ", device_id);
        process.exit(1);
    }
    else {
        device_id = device_id_int;
    }

    const port_int = parseInt(port);
    if (isNaN(port_int)) {
        console.error("Could not parse provided port to a number: ", port);
        process.exit(1);
    }
    else {
        port = port_int;
    }
    return { device_id, source, host, port };
}

function get_teensy_serial_port(source) {
    return new SerialPort(
        {
            path: source,
            baudRate: 5000000
        }
    );
}

function main(source, network_sync_host, network_sync_port, device_id) {
    const teensy_serial_port = get_teensy_serial_port(source);
    const parser = teensy_serial_port.pipe(new ReadlineParser({ delimiter: '\n' }));
    const client = dgram.createSocket('udp4');

    parser.on("data", (line) => {
        const line_split = line.split("\t");
        const network_obj = { "time": parseInt(line_split[0]), "deviceId": device_id, line: line };
        const network_str = JSON.stringify(network_obj);
        client.send(network_str, network_sync_port, network_sync_host);
        // write to tmp
        fs.appendFile(
            `/tmp/serial-data-device-${device_id}.dat`, network_str + '\n'
        );
    });

    teensy_serial_port.write("somejunktoget itstarted");

    return teensy_serial_port;
}

const args = process_args();
// invoke main
main(args.source, args.host, args.port, args.device_id);