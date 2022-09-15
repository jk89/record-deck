const process = require('process');
const fs = require("fs");
const net = require("net");
const server = new net.Server();
const path = require('path');

/**
 * A function to process this programs cli arguments and throws meaningful errors if validation fails. 
 * @return {{run_id: string, port: number}}
 *  Returns a arguments object, with members: 
 *    - run_id [string], a name for the merged collected data to be stored within the ./datasets/data/calibration-data/[run_id].jsonl file. e.g. 'august_20_experiment_1'.
 *    - port [number], port for which this program will listen for data at, e.g. 8132.
 */
function process_args() {
    // validate number of arguments
    if (process.argv.length !== 4) {
        console.error("Expected 2 argument: [port (e.g. 8132), run_id (e.g. august_20_experiment_1)]");
        process.exit(1);
    }

    // unpack expected number of arguments
    let [port, run_id] = process.argv.slice(2, 4);

    // try and parse port as int
    const port_int = parseInt(port);
    if (isNaN(port_int)) {
        console.error("Could not parse provided port to a number: ", port);
        process.exit(1);
    }
    else {
        port = port_int;
    }

    // require run_id to be truthy string e.g. "" is not valid
    if (!run_id) {
        console.error(`Need to provide a valid run_id given '${run_id}'`);
        process.exit(1);
    }

    // return args object
    return { port, run_id };
}

// Bind to the servers listening callback, print some useful information when it fires.
server.on('listening', () => {
    var address = server.address();
    var port = address.port;
    var family = address.family;
    var ip_address = address.address;
    console.log('Server is listening at port' + port);
    console.log('Server ip :' + ip_address);
    console.log('Server is IP4/IP6 : ' + family);
});

// Process cli program arguments
const args = process_args();
const run_folder_location = `datasets/data/calibration-data/${args.run_id}`;

if (fs.existsSync(run_folder_location)) {
    throw `Folder '${run_folder_location}' already exists! Exiting!`
}
else {
    const dir = path.resolve(path.join(__dirname, run_folder_location));
    fs.mkdirSync(dir);
}
// check if a folder exists for this run already
// fs fs.existsSync(dir)

// Define global to hold all recieved data from each network device.
/** @type {Array<{line: string, deviceId: number, time: number}>} */
const file_data = [];

let debounce = 0;
/**
 * Function to save the retrieved file_data from both hosts and save it to a new jsonl file, to be saved at this location: datasets/data/calibration-data/[run_id].jsonl. Finally
 * after file is saved exit program. 
 * @param {{run_id: string, port: number}} args
 * An argument object, with members: 
 *  - run_id [string], a name for the merged collected data to be stored within the ./datasets/data/calibration-data/[run_id].jsonl file. e.g. 'august_20_experiment_1'.
 *  - port [number], port for which this program will listen for data at, e.g. 8132.
 */
function shutdown(args) {
    const out_data_location = `datasets/data/calibration-data/${args.run_id}/raw_capture_data.jsonl`;
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

// bind shutdown to Ctrl-c signal
process.on('SIGINT', () => {
    shutdown(args);
});

let connection_ctr = 0;
let completed_connections = 0;
// Create a server connection callback to deal with newly connected clients.
server.on("connection", (socket) => {
    // add connection
    connection_ctr++;

    // reject for more than two connections encoder+adc
    if (connection_ctr > 2) {
        throw "Too many connections";
    }

    // for new data recieved from a client add this to a string buffer.
    let buffer = "";
    socket.on("data", (msg) => {
        const msg_str = msg.toString();
        buffer += msg_str;
    });

    // when the client ends the connection
    socket.on("end", () => {
        console.log("Client ended connection: ", connection_ctr);
        console.log("buffer", buffer);
        // parse recieved data
        const msg = JSON.parse(buffer);
        console.log("complete message", msg);
        // indicate this is now a completed connection as data transfer has finished and client has requested termination of the connection.
        completed_connections++;

        // add the recieved data to the file data.
        msg.forEach((line_data) => {
            file_data.push(line_data);
        });

        // when both devices have closed call shutdown.
        if (completed_connections == 2) {
            // got all datasets
            console.log("got all data proceeding with shutdown");
            shutdown(args);
        }
    });

    // On socket error print it and close the server.
    socket.on("error", (err) => {
        console.error("Error:", err, err.stack);
        server.close();
    });
});

// Start the server listening on args.port. Print some useful information about the host.
server.listen(args.port, () => {
    const address = server.address();
    const port = address.port;
    const family = address.family;
    const ip_address = address.address;
    console.log('Server is listening at port' + port);
    console.log('Server ip :' + ip_address);
    console.log('Server is IP4/IP6 : ' + family);
});
