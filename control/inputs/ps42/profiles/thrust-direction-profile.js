const ProfileTypes = [
    "thrust-direction"
];
class Profile{
    type = "unknown";
    handleInput(inputObj) {}
}

class ThrustDirectionProfile extends Profile {
    type="thrust-direction";
    state = {thrust:0, direction: true}; //cw true / ccw false
    handleInput(inputObj) {
        if (inputObj.type === "trigger" && inputObj.label === "r2") {
            // we have a trigger thrust value to update
            this.state.thrust = inputObj.value;
        }
        // triangle up
        else if (inputObj.type === "button" && inputObj.label === "triangle" && inputObj.value === false) {
            // invert direction
            this.state.direction = !this.state.direction
        }

        console.log("currentState", this.state);
    }
}

export { ThrustDirectionProfile };