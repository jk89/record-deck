const dgram = require('dgram');
const process = require('process');
const { SerialPort, ReadlineParser } = require('serialport');
const fs_promise = require('fs/promises');
const fs = require("fs");

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

const args = process_args();
const file_data = [];



function main(source, network_sync_host, network_sync_port, device_id) {
    const teensy_serial_port = get_teensy_serial_port(source);

    const parser = teensy_serial_port.pipe(new ReadlineParser({ delimiter: '\n' }));
    const client = dgram.createSocket('udp4');
    let data_ctr = 0;

    fs.rmSync(`/tmp/serial-data-device-${device_id}.dat`, {
        force: true,
    });

    let resolver = Promise.resolve();

    parser.on("data", (line) => {
        if (device_id == 1) {
            const line_split = line.split("\t");
            const time = parseInt(line_split[0]);
            if (!isNaN(time) && time != null) {
                const network_obj = { "time": time, "deviceId": device_id, line: line };
                // const network_str = JSON.stringify(network_obj);
                // client.send(network_str, network_sync_port, network_sync_host);
                // console.log(JSON.stringify(network_obj));
                file_data.push(network_obj);
            }
        }
        else if (device_id == 0) {
            // device_id 0
            // this is to force it to keep order
            resolver = resolver.then(() => {
                const network_obj = { "time": data_ctr, "deviceId": device_id, line: `${data_ctr}\t${line}` };
                // console.log(JSON.stringify(network_obj));
                file_data.push(network_obj);
                data_ctr += 1;
            });
        }
        else {
            throw "Device_id can be 1 or 0";
        }
        
    });

    teensy_serial_port.on("close", async () => {
        await shutdown(args, resolver);
    });

    teensy_serial_port.write("somejunktoget itstarted");

    return resolver;
}



// invoke main
const resolution = main(args.source, args.host, args.port, args.device_id); // .then(console.log)

let debounce = 0;
async function shutdown(args, resolution) {
    if (debounce < 1) {
        const out_data_location = `/tmp/serial-data-device-${args.device_id}.jsonl`;

        console.log(`The server is shutting down.`);
        console.log("Please wait why we flush received data to disk...");
    
        try {
            await resolution;
            const file_str = file_data.map((line_data) => {
                return JSON.stringify(line_data);
            }).join("\n");
            fs.writeFileSync(out_data_location, file_str);
            console.log("Shutdown complete ✅");
            process.exit(0);
        }
        catch (err) {
            console.log("Flush failed... shutting down anyway ❌");
            console.error(err, err.stack);
            process.exit(0);
        }

    }
    debounce++;
}


process.on('SIGINT', async () => {
    await shutdown(args, resolution);
});


// write to tmp
/*fs_promise.appendFile(
    `/tmp/serial-data-device-${device_id}.dat`, network_str + '\n'
);*/