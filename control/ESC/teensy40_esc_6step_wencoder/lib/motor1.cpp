#define PIN_A_IN 2
#define PIN_B_IN 9
#define PIN_C_IN 8

#define PIN_A_SD 1
#define PIN_B_SD 0
#define PIN_C_SD 7 // watchout for ADC sync pin needs to be changed

#define PWM_FREQUENCY 36000

// import state map

#include "calibration_state_map/motor1/commutation_state_locywrlyvnkdzevorzyr.cpp"

/*
// Combined state map CW and CCW over 16384 angular steps
const uint32_t STATE_MAP[2][16384] = {
    CW_STATE_MAP,
    CCW_STATE_MAP,
};
*/

void init_motor1_pwm() {
    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY);
    digitalWriteFast(PIN_A_IN, LOW);
    digitalWriteFast(PIN_B_IN, LOW);
    digitalWriteFast(PIN_C_IN, LOW);
    analogWrite(PIN_A_SD, LOW);
    analogWrite(PIN_B_SD, LOW);
    analogWrite(PIN_C_SD, LOW);
}

bool STARTUP_MODE = true;

/*
What do the states mean
0: A_IN, B_SD
1: A_IN, C_SD
2: B_IN, C_SD
3: B_IN, A_SD
4: C_IN, A_SD
5: C_IN, B_SD
*/

void enforce_motor1_state(int state) {
    if (state == 0) {

    }
    else if (state == 1) {

    }
    else if (state == 2) {

    }
    else if (state == 3) {

    }
    else if (state == 4) {

    }
    else if (state == 5) {
        
    }
}