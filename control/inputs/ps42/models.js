/*
Abstraction

InputModel -> Controller -> [ModelOutputs]
e.g.
DualShockToThrustDirection -> Controller -> [ThrustDirectionToSerialPort]

The input model builds some state, the controller is informed of updates to the state, the controller distributes the inputs to the outputs
the outputs decide what to do with the newly changed state, e.g. send it to a serialport or some network port etc.
*/

const ProfileTypes = {
    ThrustDirection: "thrust-direction"
}

const InputTypes = {
    DualShock: "dualshock",
    UDP: "upd"
}

const OutputTypes = {
    Serial: "serial",
    UDP: "upd"
}

class InputToModelBase {
    type = null; // e.g. dualshock/UDP
    profile = null; // e.g. "thrust-direction"
    state = null;
    scale = null;
    controllerInst = null;
    async start () {}
    async handleInput(stateObj) {
        await this?.controllerInst?.emitToOutputs(stateObj);
    }
}

class ModelToOutputBase {
    type = null; // e.g. serial/UDP
    profile = null; // e.g. "thrust-direction"
    async ready() {}
    async handleOutput(inputObj) {}
}

class InputOutputController {
    inputController = null;
    outputControllers = [];
    oldStateData = null;

    async emitToOutputs(stateData) {
        const stateDataStr = JSON.stringify(stateData);
        if (this.oldStateData !== stateDataStr) {
            await Promise.all(this.outputControllers.map((outputController) => outputController.handleOutput(stateData)));
            this.oldStateData = stateDataStr;
        }
    }

    async start() {
        await Promise.all(this.outputControllers.map((outputController => outputController.ready())));
        await this.inputController.ready();
    }

    constructor(inputToModelInst, modelToOutputInsts) {
        this.inputController = inputToModelInst;
        this.outputControllers = modelToOutputInsts;

        // attach this to input controller
        this.inputController.controllerInst = this;
    }
}

module.exports = { ProfileTypes, InputTypes, OutputTypes, InputToModelBase, ModelToOutputBase, InputOutputController }