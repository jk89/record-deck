const { InputTypes, ProfileTypes, InputToModelBase } = require("../../../core");

class DualShockToThrustDirectionModel extends InputToModelBase {
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

        // triangle up... we have a direction to reverse... only if thrust is zero otherwise risk breaking the hardware
        else if (inputObj.type === "button" && inputObj.label === "triangle" && inputObj.value === false && this.state.thrust === 0) this.state.direction = !this.state.direction

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

module.exports = { DualShockToThrustDirectionModel }