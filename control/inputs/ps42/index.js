const { ProfileTypes, InputTypes, OutputTypes, InputToModelBase, ModelToOutputBase, InputOutputController } = require("./models");
const { DualShockToThrustDirection } = require("./thrust-direction/inputs/dualshock"); // FIXME do this in thrust direction index and only unpack modules here
const { ThrustDirectionToSerialPort } = require("./thrust-direction/outputs/serialport");

module.exports = {
    types: {
        ProfileTypes, InputTypes, OutputTypes
    },
    controllers: {
        InputToModelBase, ModelToOutputBase, InputOutputController
    },
    inputs: {
        DualShockToThrustDirection
    },
    outputs: {
        ThrustDirectionToSerialPort
    }
}