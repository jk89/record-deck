const { DualShockToThrustDirection } = require("../inputs/dualshock");
const { ThrustDirectionToSerialPort } = require("../outputs/serialport");
const { InputOutputController } = require("../../../models");

const ThrustDirectionController = new InputOutputController(new DualShockToThrustDirection({scale: 60.0 / 255.0}), [new ThrustDirectionToSerialPort()]);
ThrustDirectionController.start().then(console.log).catch(console.error);