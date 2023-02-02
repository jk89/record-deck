const { DualShockThrustDirectionModel } = require("../inputs/dualshock");
const { ThrustDirectionModelSerialPort } = require("../outputs/serialport");
const { InputOutputController } = require("../../../models");

const ThrustDirectionController = new InputOutputController(new DualShockThrustDirectionModel({scale: 60.0 / 255.0}), [new ThrustDirectionModelSerialPort()]);
ThrustDirectionController.start().then(console.log).catch(console.error);