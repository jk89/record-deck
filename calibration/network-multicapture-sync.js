// const dgram = require('dgram');
// const server = dgram.createSocket('udp4');
const process = require('process');
const fs = require("fs");
const net = require('net');
const server = new net.Server();

function process_args() {
    console.log(process.argv);
    if (process.argv.length !== 4) {
        console.error("Expected 2 argument: [port (e.g. 8132), run_id (e.g. 1)]");
        process.exit(1);
    }
    let [port, run_id] = process.argv.slice(2, 4);

    const port_int = parseInt(port);
    if (isNaN(port_int)) {
        console.error("Could not parse provided port to a number: ", port);
        process.exit(1);
    }
    else {
        port = port_int;
    }

    if (!run_id) {
        console.error(`Need to provide a valid run_id given '${run_id}'`);
        process.exit(1);
    }

    return { port, run_id };
}

const args = process_args();

const out_data_location = `datasets/data/calibration-data/run_${args.run_id}.jsonl`;
const file_data = [];

let debounce = 0;
process.on('SIGINT', () => {
    if (debounce < 1) {
        console.log(`The server is shutting down.`);
        console.log("Please wait why we flush received data to disk...");
        const file_str = file_data.map((line_data) => {
            return JSON.stringify(line_data);
        }).join("\n");
        fs.writeFileSync(out_data_location, file_str);
        console.log("Shutdown complete ✅");
        process.exit(0);
    }

    debounce++;
});

let last_time_device_0 = 0;
let last_time_device_1 = 0;
let largest_diff = 0;

server.on('connection', (socket) => {
    console.log("New connection");

    let left_overs = "";
    socket.on('data', (msg) => {
        const msg_str = msg.toString();
        console.log("msg_strmsg_strmsg_str");
        console.log(`'''${msg_str}'''`);
        
        const data = JSON.parse(msg_str);
        // console.log("datadatadata", data);
        if (data["deviceId"] == 0) {
            last_time_device_0 = data["time"];
        }
        else if (data["deviceId"] == 1) {
            last_time_device_1 = data["time"];
        }
        current_difference = last_time_device_0 - last_time_device_1;
        current_difference_magnitude = Math.abs(current_difference);
        if (current_difference_magnitude)
            largest_diff = current_difference_magnitude;
    
        const data2 = { "ctime": data["time"], "deviceId": data["deviceId"], "mdiff": largest_diff, "cdiff": current_difference, "line": data["line"] }
        
        // console.log(data2);
        file_data.push(data);

    });

    socket.on('end', () => {
        console.log('Closing connection with the client');
    });

    socket.on('error', (err) => {
        console.error('Error:', err);
        server.close();
    });

});


server.listen(args.port, () => {
    var address = server.address();
    var port = address.port;
    var family = address.family;
    var ip_address = address.address;
    console.log('Server is listening at port' + port);
    console.log('Server ip :' + ip_address);
    console.log('Server is IP4/IP6 : ' + family);
});
