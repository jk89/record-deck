const { Controller, DualShockToThrustDirection, ThrustDirectionToSerialProfile} = require("./controller");

const ThrustDirectionController = new Controller(new DualShockToThrustDirection({scale: 60.0 / 255.0}), [new ThrustDirectionToSerialProfile()]);
ThrustDirectionController.start().then(console.log).catch(console.error);