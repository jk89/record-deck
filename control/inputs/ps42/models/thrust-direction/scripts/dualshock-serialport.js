const { DualShockToThrustDirectionModel } = require("../inputs/dualshock");
const { ThrustDirectionModelToSerialPort } = require("../outputs/serialport");
const { InputOutputController } = require("../../../core");

const ThrustDirectionController = new InputOutputController(new DualShockToThrustDirectionModel({scale: 20.0 / 255.0}), [new ThrustDirectionModelToSerialPort()]);
ThrustDirectionController.start().then(console.log).catch(console.error);