// const { Controller, DualShockToThrustDirection, ThrustDirectionToSerialProfile} = require("./controller");
const { DualShockToThrustDirection } = require("../inputs/dualshock");
const { ThrustDirectionToSerialProfile } = require("../outputs/serialport");
const { InputOutputController } = require("../models");

const ThrustDirectionController = new InputOutputController(new DualShockToThrustDirection({scale: 60.0 / 255.0}), [new ThrustDirectionToSerialProfile()]);
ThrustDirectionController.start().then(console.log).catch(console.error);