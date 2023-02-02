const { SerialPort, ReadlineParser } = require('serialport');
const Struct = require('typed-struct').default;
const { OutputTypes, ProfileTypes, ModelToOutputBase } = require("../../../models");

class ThrustDirectionModelToSerialPort extends ModelToOutputBase {
    type = OutputTypes.Serial
    profile = ProfileTypes.ThrustDirection
    lastSerialData = null;
    lastWordStr = null;
    ThrustDirectionStructure = new Struct('ThrustDirection')
    .UInt8("direction")
    .UInt8("thrust")
    .compile();

    async ready () {
        const serialOptions = {baudRate: 5000000};

        const serialPorts = await SerialPort.list();

        let successfulPortObj = false;
        if (this.serialOptions) {
            if (this.serialOptions.hasOwnProperty("path")) successfulPortObj = serialPorts.find((it) => it.path == this.serialOptions.path);
            if (this.serialOptions.hasOwnProperty("baudRate")) serialOptions.baudRate = this.serialOptions.baudRate;
        }

        if (!successfulPortObj) {
            // the user provided one failed... attempt to find one
            const relevantPorts = serialPorts.filter((it) => it.path.includes("/dev/ttyACM"));
            if (!relevantPorts.length) throw "Could not find any serial ports to write too!";
            successfulPortObj = relevantPorts[0];
        }

        /* successfulPortObj looks like:
            path: '/dev/ttyACM0',
            manufacturer: 'Teensyduino',
            serialNumber: '13059120',
            pnpId: 'usb-Teensyduino_USB_Serial_13059120-if00',
            locationId: undefined,
            vendorId: '16c0',
            productId: '0483'
        */

        // #TODO should validate its a teensy40
        
        // update options with new path
        if (successfulPortObj) serialOptions.path = successfulPortObj.path;
        this.serialOptions = serialOptions;

        // init serial port
        this.serialport = new SerialPort(this.serialOptions);

        // bind events
        this.serialport.on("close", () => {
            console.log("Serial port closed");
            process.exit();
        });
        this.serialparser = this.serialport.pipe(new ReadlineParser({ delimiter: '\n' }));
        this.serialparser.on("data", (line) => {
            if (line !== this.lastSerialData) {
                console.log("got new serial data", line);
                this.lastSerialData = line;
            }
        });
    }

    async handleOutput(inputState) {
        const word = new this.ThrustDirectionStructure();
        word.direction = inputState.direction === true ? 0 : 1;
        word.thrust = inputState.thrust;
        const newWordBytes = word.$raw;
        const newWordBytesCompare = JSON.stringify(newWordBytes);
        if (newWordBytesCompare !== this.lastWordStr) {
            // emit to serial device
            this.serialport.write(newWordBytes);
            this.lastWordStr = newWordBytesCompare;
        }
    }

    constructor (serialOptions) {
        super();
        this.serialOptions = serialOptions;
    }
}

module.exports = { ThrustDirectionModelToSerialPort }