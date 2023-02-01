
const { SerialPort, ReadlineParser } = require('serialport');
const Struct = require('typed-struct').default;

const ProfileTypes = [
    "thrust-direction"
];
class Profile{
    type = "unknown";
    handleInput(inputObj) {}
}

const stateChanged = (oldState, newState) => {
    if (JSON.stringify(oldState) !== JSON.stringify(newState)) return true;
    else return false;
}

class ThrustDirectionProfile extends Profile {
    type="thrust-direction";
    state = {thrust:0, direction: false}; //cw false / ccw true

    // create profile struct
    ThrustDirectionStructure = new Struct('ThrustDirection') // give a name to the constructor
    /*.Bits16({
        // [offset, length]
        direction: [0, 1], // 1 bit direction
        thrust: [1,12] // 12 bit thrust
    })        // signed 8-bit integer field `foo`*/
    .UInt8("direction")
    .UInt8("thrust")
    .compile();         // create a constructor for the structure, called last

    stateToProfileWord() {
        const word = new this.ThrustDirectionStructure();
        const va = this.state.direction; //  === true ? 0x1 : 0x0;
        word.direction = va;
        word.thrust = this.state.thrust;
        return word.$raw;
    }

    handleInput(inputObj) {
        const oldState = Object.assign({}, this.state);
        if (inputObj.type === "trigger" && inputObj.label === "r2") {
            // we have a trigger thrust value to update
            this.state.thrust = inputObj.value;
        }
        // triangle up
        else if (inputObj.type === "button" && inputObj.label === "triangle" && inputObj.value === false) {
            // invert direction
            this.state.direction = !this.state.direction
        }

        if (stateChanged(oldState, this.state)) {
            // console.log("changedState", this.state);
            return this.stateToProfileWord();
        }
        else return false;
    }
}

// --------------------------------------------------------------------------

const inputTypes = {
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

class Controller{
 gamepad = null;
 device = null;
 serialOptions = null;
 serialport = null;
 serialparser = null;

 start() {
    this.serialOptions = this.serialOptions || { path: '/dev/ttyACM0', baudRate: 5000000 };
    this.serialport = new SerialPort(this.serialOptions); // serialport.write('ROBOT POWER ON')
    this.serialport.on("close", async () => {
        console.log("Serial port closed");
        process.exit();
    });
    this.serialparser = this.serialport.pipe(new ReadlineParser({ delimiter: '\n' }));
    this.lastSerialData = null;
    this.serialparser.on("data", (line) => {
        if (line !== this.lastSerialData ) {
            this.lastSerialData = line;
            console.log("got serial data", line);
        }
    });
    const gamepad = this.ds.open(this.device, {smoothAnalog:10, smoothMotion:15, joyDeadband:4, moveDeadband:4});
    gamepad.onmotion=true; gamepad.onstatus=true;
    gamepad.ondigital = (button, value) => {
        this.parseInput({
            type: "button",
            label: button,
            value
        })
    }
    gamepad.onanalog = (axis, value) => {
        this.parseInput({
            type: inputTypes[axis],
            label: axis,
            value
        })
    }
 }

 profileHandler = null;
 constructor(ds, ProfileHandler, serialOptions) {
    if (!ds) { console.log("Need to provide a dualshock lib instance"); process.exec(); }
    this.ds = ds;
    const devices = this.ds.getDevices();
    if(devices.length < 1) { console.log("Could not find a controller!"); process.exit(); }
    this.device = devices[0];
    if (!ProfileHandler) { console.log("Need to provide a profile handler"); process.exec(); }
    this.profileHandler = new ProfileHandler();
 }

 parseInput(input) {
    const byteString = this.profileHandler.handleInput(input);
    if (byteString) {
        console.log("byteString", byteString);
        this.serialport.write(byteString);
    }
 }
}

async function init() {
    const ds = await import("dualshock");
    const ThrustDirectionController = new Controller(ds, ThrustDirectionProfile);
    ThrustDirectionController.start();
}

init().then(console.log).catch(console.error);