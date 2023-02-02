const { ProfileTypes, InputTypes, OutputTypes, InputToModelBase, ModelToOutputBase, InputOutputController } = require("./models");
const { DualShockThrustDirectionModel } = require("./thrust-direction/inputs/dualshock"); // FIXME do this in thrust direction index and only unpack modules here
const { ThrustDirectionModelSerialPort } = require("./thrust-direction/outputs/serialport");

module.exports = {
    types: {
        ProfileTypes, InputTypes, OutputTypes
    },
    controllers: {
        InputToModelBase, ModelToOutputBase, InputOutputController
    },
    inputs: {
        DualShockThrustDirectionModel
    },
    outputs: {
        ThrustDirectionModelSerialPort
    }
}