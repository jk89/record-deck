const process = require('process');
const fs = require("fs");
const net = require("net");
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

server.on('listening', () => {
    var address = server.address();
    var port = address.port;
    var family = address.family;
    var ip_address = address.address;
    console.log('Server is listening at port' + port);
    console.log('Server ip :' + ip_address);
    console.log('Server is IP4/IP6 : ' + family);
});

const args = process_args();

const file_data = [];

let debounce = 0;
function shutdown(args) {
    const out_data_location = `datasets/data/calibration-data/${args.run_id}.jsonl`;
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
}

process.on('SIGINT', () => {
    shutdown(args);
});

let connection_ctr = 0;
let completed_connections = 0;
server.on("connection", (socket) => {
    connection_ctr++;

    if (connection_ctr > 2) {
        throw "Too many connections";
    }

    let buffer = "";
    socket.on("data", (msg) => {
        const msg_str = msg.toString();
        buffer += msg_str;
    });

    socket.on("end", () => {
        console.log("Client ended connection: ", connection_ctr);
        console.log("buffer", buffer);
        const msg = JSON.parse(buffer);
        console.log("complete message", msg);
        completed_connections++;

        msg.forEach((line_data) => {
            file_data.push(line_data);
        });

        if (completed_connections == 2) {
            // got all datasets
            console.log("got all data proceeding with shutdown");
            shutdown(args);
        }
    });

    socket.on("error", (err) => {
        console.error("Error:", err, err.stack);
        server.close();
    });
});

server.listen(args.port, () => {
    const address = server.address();
    const port = address.port;
    const family = address.family;
    const ip_address = address.address;
    console.log('Server is listening at port' + port);
    console.log('Server ip :' + ip_address);
    console.log('Server is IP4/IP6 : ' + family);
});
