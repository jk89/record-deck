const { ProfileTypes, InputTypes, OutputTypes, InputToModelBase, ModelToOutputBase, InputOutputController } = require("./core");
const { DualShockToThrustDirectionModel } = require("./models/thrust-direction/inputs/dualshock"); // FIXME do this in thrust direction index and only unpack modules here
const { ThrustDirectionModelToSerialPort } = require("./models/thrust-direction/outputs/serialport");

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