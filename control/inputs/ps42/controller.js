
const { SerialPort, ReadlineParser } = require('serialport');
const Struct = require('typed-struct').default;

/*
Abstraction

InputModel -> Controller -> [ModelOutputs]
e.g.
DualShockToThrustDirection -> Controller -> [ThrustDirectionToSerialProfile]

The input model builds some state, the controller is informed of updates to the state, the controller distributes the inputs to the outputs
the outputs decide what to do with the newly changed state, e.g. send it to a serialport or some network port etc.
*/

const ProfileTypes = {
    ThrustDirection: "thrust-direction"
}

const InputTypes = {
    DualShock: "dualshock",
    UDP: "upd"
}

const OutputTypes = {
    Serial: "serial",
    UDP: "upd"
}
    

class InputToModel {
    type = null; // e.g. dualshock/UDP
    profile = null; // e.g. "thrust-direction"
    state = null;
    scale = null;
    async start () {}
    controllerInst = null;
    async handleInput(stateObj) {
        await this?.controllerInst?.emitToOutputs(stateObj);
    }
}
class ModelToOutput {
    type = null; // e.g. serial/UDP
    profile = null; // e.g. "thrust-direction"
    async ready() {}
    async handleOutput(inputObj) {}
}

class DualShockToThrustDirection extends InputToModel {
    type = InputTypes.DualShock;
    profile = ProfileTypes.ThrustDirection
    inputTypes = {
        "rStickX": "stick",
        "rStickY": "stick",
        "lStickX": "stick",
        "lStickY": "stick",
        "button": "button",
        "l2": "trigger",
        "r2": "trigger",
        "t1X": "track",
        "t1Y": "track"
    };
    ds = null;
    gamepad = null;
    gamepadArgs = null;
    scale = 1;
    state = { thrust: 0, direction: true }; //cw 0 false / ccw 1 true

    async handleInput(inputObj) {
        // r2 trigger... we have a thrust value to update
        if (inputObj.type === "trigger" && inputObj.label === "r2") this.state.thrust = inputObj.value * this.scale;

        // triangle up... we have a direction to reverse
        else if (inputObj.type === "button" && inputObj.label === "triangle" && inputObj.value === false) this.state.direction = !this.state.direction

        // emit state to controller
        await super.handleInput(this.state);
    }
    
    async ready() {
        this.ds = await import("dualshock");

        const devices = this.ds.getDevices();
        if (devices.length < 1) throw "Could not find a controller!";
        this.device = devices[0];

        this.gamepad= this.ds.open(this.device, this.gamepadArgs);
        this.gamepad.onmotion = true; this.gamepad.onstatus = true;
        this.gamepad.ondigital = async (label, value) => this.handleInput({ type: "button", label, value });
        this.gamepad.onanalog = async (label, value) => this.handleInput({ type: this.inputTypes[label], label, value});
    }

    constructor(args) {
        super();
        const gamepadArgs = { smoothAnalog: 10, smoothMotion: 15, joyDeadband: 4, moveDeadband: 4 };
        if (args) {
            if (args.hasOwnProperty && args.hasOwnProperty("scale")) this.scale = args.scale;
            if (args.hasOwnProperty && args.hasOwnProperty("smoothAnalog")) gamepadArgs.smoothAnalog = args.smoothAnalog;
            if (args.hasOwnProperty && args.hasOwnProperty("smoothMotion")) gamepadArgs.smoothMotion = arg.smoothMotion;
            if (args.hasOwnProperty && args.hasOwnProperty("joyDeadband"))  gamepadArgs.joyDeadband = arg.joyDeadband;
            if (args.hasOwnProperty && args.hasOwnProperty("moveDeadband")) gamepadArgs.moveDeadband = args.moveDeadband;
        }
        this.gamepadArgs = gamepadArgs;
    }
}

class ThrustDirectionToSerialProfile extends ModelToOutput {
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

class Controller {
    inputController = null;
    outputControllers = [];
    oldStateData = null;

    async emitToOutputs(stateData) {
        const stateDataStr = JSON.stringify(stateData);
        if (this.oldStateData !== stateDataStr) {
            await Promise.all(this.outputControllers.map((outputController) => outputController.handleOutput(stateData)));
            this.oldStateData = stateDataStr;
        }
    }

    async start() {
        await Promise.all(this.outputControllers.map((outputController => outputController.ready())));
        await this.inputController.ready();
    }

    constructor(inputToModelInst, modelToOutputInsts) {
        this.inputController = inputToModelInst;
        this.outputControllers = modelToOutputInsts;

        // attach this to input controller
        this.inputController.controllerInst = this;
    }
}

module.exports = {
    Controller,
    InputToModel,
    DualShockToThrustDirection,
    ThrustDirectionToSerialProfile,
    ModelToOutput
}