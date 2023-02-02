const { ProfileTypes, InputTypes, OutputTypes, InputToModelBase, ModelToOutputBase, InputOutputController } = require("./models");
const { DualShockToThrustDirection } = require("./inputs/dualshock");
const { ThrustDirectionToSerialPort } = require("./outputs/serialport");

module.exports = {
    types: {
        ProfileTypes, InputTypes, OutputTypes
    },
    controllers: {
        InputToModelBase, ModelToOutputBase, InputOutputController
    }
}