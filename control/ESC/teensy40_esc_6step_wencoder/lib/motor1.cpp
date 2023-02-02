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
// Combined state map looks like this.... CW and CCW over 16384 angular steps
const uint32_t STATE_MAP[2][16384] = {
    CW_STATE_MAP,
    CCW_STATE_MAP,
};
*/

bool STARTUP_MODE = true;

void init_motor1_pwm()
{
    STARTUP_MODE = true;
    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY);
    digitalWriteFast(PIN_A_IN, LOW);
    digitalWriteFast(PIN_B_IN, LOW);
    digitalWriteFast(PIN_C_IN, LOW);
    analogWrite(PIN_A_SD, LOW);
    analogWrite(PIN_B_SD, LOW);
    analogWrite(PIN_C_SD, LOW);
}

int MOTOR_1_STATE = 0;

/*
What do the states mean
0: A_IN, B_SD
1: A_IN, C_SD
2: B_IN, C_SD
3: B_IN, A_SD
4: C_IN, A_SD
5: C_IN, B_SD
*/

// TEST we use digitalWriteFast to turn of the SD pins? it should be quicker!

void enforce_motor1_state(int state)
{
    if (state == 0) // 0: A_IN, B_SD
    {
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        analogWrite(PIN_A_SD, 0);
        analogWrite(PIN_C_SD, 0);

        digitalWriteFast(PIN_A_IN, HIGH);
        analogWrite(PIN_B_SD, THRUST);
    }
    else if (state == 1) // 1: A_IN, C_SD
    {
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        analogWrite(PIN_A_SD, 0);
        analogWrite(PIN_B_SD, 0);

        digitalWriteFast(PIN_A_IN, HIGH);
        analogWrite(PIN_C_SD, THRUST);
    }
    else if (state == 2) // 2: B_IN, C_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        analogWrite(PIN_A_SD, 0);
        analogWrite(PIN_B_SD, 0);

        digitalWriteFast(PIN_B_IN, HIGH);
        analogWrite(PIN_C_SD, THRUST);
    }
    else if (state == 3) // 3: B_IN, A_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        analogWrite(PIN_B_SD, 0);
        analogWrite(PIN_C_SD, 0);

        digitalWriteFast(PIN_B_IN, HIGH);
        analogWrite(PIN_A_SD, THRUST);
    }
    else if (state == 4) // 4: C_IN, A_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_B_IN, LOW);
        analogWrite(PIN_B_SD, 0);
        analogWrite(PIN_C_SD, 0);

        digitalWriteFast(PIN_C_IN, HIGH);
        analogWrite(PIN_A_SD, THRUST);        
    }
    else if (state == 5) // 5: C_IN, B_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_B_IN, LOW);
        analogWrite(PIN_A_SD, 0);
        analogWrite(PIN_C_SD, 0);

        digitalWriteFast(PIN_C_IN, HIGH);
        analogWrite(PIN_B_SD, THRUST);          
    }
}