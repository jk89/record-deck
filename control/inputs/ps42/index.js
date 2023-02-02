const { ProfileTypes, InputTypes, OutputTypes, InputToModelBase, ModelToOutputBase, InputOutputController } = require("./models");
const { DualShockToThrustDirectionModel } = require("./thrust-direction/inputs/dualshock"); // FIXME do this in thrust direction index and only unpack modules here
const { ThrustDirectionModelToSerialPort } = require("./thrust-direction/outputs/serialport");

module.exports = {
    types: {
        ProfileTypes, InputTypes, OutputTypes
    },
    controllers: {
        InputToModelBase, ModelToOutputBase, InputOutputController
    },
    inputs: {
        DualShockToThrustDirectionModel
    },
    outputs: {
        ThrustDirectionModelToSerialPort
    }
}