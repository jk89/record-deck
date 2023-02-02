const { DualShockToThrustDirectionModel } = require("../inputs/dualshock");
const { ThrustDirectionModelToSerialPort } = require("../outputs/serialport");
const { InputOutputController } = require("../../../models");

const ThrustDirectionController = new InputOutputController(new DualShockToThrustDirectionModel({scale: 60.0 / 255.0}), [new ThrustDirectionModelToSerialPort()]);
ThrustDirectionController.start().then(console.log).catch(console.error);