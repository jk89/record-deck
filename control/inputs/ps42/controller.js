
const { SerialPort, ReadlineParser } = require('serialport');
const Struct = require('typed-struct').default;

/*
Abstraction

InputModel -> Controller -> [ModelOutputs]
e.g.
DualShockToThrustDirection -> Controller -> [ThrustDirectionToSerialProfile]
*/

const ProfileTypes = {
    ThrustDirection: "thrust-direction"
}

const InputTypes = {
    DualShock: "dualshock",
    Udp: "upd"
}

const OutputTypes = {
    Serial: "serial",
    Udp: "upd"
}
    

class InputToModel {
    type = null; // e.g. dualshock/udp
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
    type = null; // e.g. serial/udp
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
        if (inputObj.type === "trigger" && inputObj.label === "r2") {
            this.state.thrust = inputObj.value * this.scale;
        }
        // triangle up... we have a direction to reverse
        else if (inputObj.type === "button" && inputObj.label === "triangle" && inputObj.value === false) {
            this.state.direction = !this.state.direction
        }

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
        this.gamepad.ondigital = async (button, value) => this.handleInput(
            {
                type: "button",
                label: button,
                value
            }
        );
        this.gamepad.onanalog = async (axis, value) => this.handleInput(
            {
                type: this.inputTypes[axis],
                label: axis,
                value
            }
        );
    }

    constructor(args) {
        super();
        const gamepadArgs = { smoothAnalog: 10, smoothMotion: 15, joyDeadband: 4, moveDeadband: 4 };
        if (args) {
            if (args.hasOwnProperty && args.hasOwnProperty("scale")) this.scale = args.scale;
            if (args.hasOwnProperty && args.hasOwnProperty("smoothAnalog")) {
                gamepadArgs.smoothAnalog = args.smoothAnalog;
            }
            if (args.hasOwnProperty && args.hasOwnProperty("smoothMotion")) {
                gamepadArgs.smoothMotion = arg.smoothMotion;
            }
            if (args.hasOwnProperty && args.hasOwnProperty("joyDeadband")) {
                gamepadArgs.joyDeadband = arg.joyDeadband;
            }
            if (args.hasOwnProperty && args.hasOwnProperty("moveDeadband")) {
                gamepadArgs.moveDeadband = args.moveDeadband;
            }
        }
        this.gamepadArgs = gamepadArgs;
    }
}

class ThrustDirectionToSerialProfile extends ModelToOutput {
    type = OutputTypes.Serial
    profile = ProfileTypes.ThrustDirection

    ThrustDirectionStructure = new Struct('ThrustDirection')
    .UInt8("direction")
    .UInt8("thrust")
    .compile();

    lastSerialData = null;
    async ready () {
        const serialPorts = await SerialPort.list();

        const serialOptions = {baudRate: 5000000};

        let successfulPortObj = false;
        if (this.serialOptions) {
            
            if (this.serialOptions.hasOwnProperty("path")) {
                successfulPortObj = serialPorts.find((it) => it.path == this.serialOptions.path);

            }
            if (this.serialOptions.hasOwnProperty("baudRate")) {
                serialOptions.baudRate = this.serialOptions.baudRate;
            }
        }

        if (!successfulPortObj) {
            // the user provided one failed... attempt to find one
            const relevantPorts = serialPorts.filter((it) => it.path.includes("/dev/ttyACM"));
            if (!relevantPorts.length) {
                throw "Could not find any serial ports to write too!"
            }
            successfulPortObj = relevantPorts[0];
        }

        // todo should validate its a teensy40

        /* successfulPortObj e.g.
            path: '/dev/ttyACM0',
            manufacturer: 'Teensyduino',
            serialNumber: '13059120',
            pnpId: 'usb-Teensyduino_USB_Serial_13059120-if00',
            locationId: undefined,
            vendorId: '16c0',
            productId: '0483'
        */
        
        if (successfulPortObj) {
            serialOptions.path = successfulPortObj.path;
        }

        this.serialOptions = serialOptions;
        this.serialport = new SerialPort(this.serialOptions);

        this.serialport.on("close", () => {
            console.log("Serial port closed");
            process.exit();
        });

        this.serialparser = this.serialport.pipe(new ReadlineParser({ delimiter: '\n' }));

        this.serialparser.on("data", (line) => {
            if (line !== this.lastSerialData) {
                this.lastSerialData = line;
                console.log("got new serial data", line);
            }
        });
    }

    lastWordStr = null;
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