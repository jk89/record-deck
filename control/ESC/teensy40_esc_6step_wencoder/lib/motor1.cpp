#define PIN_A_IN 2
#define PIN_B_IN 9
#define PIN_C_IN 8
#define PIN_A_SD 1
#define PIN_B_SD 0
#define PIN_C_SD 7 // watchout for ADC sync pin needs to be changed
#define PWM_FREQUENCY 36000
#define FAULT_LED_PIN 13
#define MAX_NUMBER_TRANSTION_IN_REVERSE_PERMITTED 1

bool FAULT = false;
int STATE_VALIDATOR[6][2] = {{1, 5}, {2, 0}, {3, 1}, {4, 2}, {5, 3}, {0, 4}}; // IDX 0 {NEXT EXPECTED CW, NEXT EXPECTED CCW}
int MOTOR_1_STATE = -1;
uint16_t ANGLE = 0;
int WRONG_DIRECTION_CTR = 0;
// import STATE_MAP
#include "calibration_state_map/motor1/commutation_state_locywrlyvnkdzevorzyr.cpp"
/*
// Combined state map looks like this.... CW and CCW over 16384 angular steps
const uint32_t STATE_MAP[2][16384] = {
    CW_STATE_MAP,
    CCW_STATE_MAP,
};
*/

void init_motor1()
{
    pinMode(FAULT_LED_PIN, OUTPUT);
    pinMode(PIN_A_IN, OUTPUT);
    pinMode(PIN_B_IN, OUTPUT);
    pinMode(PIN_C_IN, INPUT);
    pinMode(PIN_A_SD, OUTPUT);
    pinMode(PIN_B_SD, OUTPUT);
    pinMode(PIN_C_SD, OUTPUT);
    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY);
    digitalWriteFast(PIN_A_IN, LOW);
    digitalWriteFast(PIN_B_IN, LOW);
    digitalWriteFast(PIN_C_IN, LOW);
    analogWrite(PIN_A_SD, LOW);
    analogWrite(PIN_B_SD, LOW);
    analogWrite(PIN_C_SD, LOW);
    digitalWriteFast(FAULT_LED_PIN, LOW);
}

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

void enforce_state_motor1(int state)
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

void fault(char* reason) {
    cli();
    FAULT = true;
    THRUST = 0;
    init_motor1();
    digitalWriteFast(FAULT_LED_PIN, HIGH);
    Serial.println(reason);
    sei();
}

void loop_motor1()
{
    if (FAULT == true) {
        sleep(10000);
        return;
    }

    // put your main code here, to run repeatedly:
    if (THRUST != 0) // main loop
    {
        ANGLE = as5147p_get_sensor_value_fast();

        // get relevant state map
        int motor1_new_state = STATE_MAP[DIRECTION][ANGLE]; // 16384

        if (motor1_new_state != MOTOR_1_STATE)
        {
            // we have a new state
            if (MOTOR_1_STATE != -1)
            { 
                // validate motor state
                int expected_new_state = STATE_VALIDATOR[MOTOR_1_STATE][DIRECTION];
                int expected_new_state_if_reversed = STATE_VALIDATOR[MOTOR_1_STATE][REVERSED_DIRECTION];

                if (expected_new_state == motor1_new_state) {
                    WRONG_DIRECTION_CTR = 0;
                }
                else if (motor1_new_state == expected_new_state_if_reversed) {
                    WRONG_DIRECTION_CTR++;
                    if (WRONG_DIRECTION_CTR > MAX_NUMBER_TRANSTION_IN_REVERSE_PERMITTED) {
                        // FAULT WRONG DIRECTION
                        fault("Wrong Direction");
                        return;
                    }
                }
                else {
                    // FAULT SKIPPED STEPS
                    fault("Skipped Steps");
                    return;
                }
            }

            // enforce commutation
            enforce_state_motor1(motor1_new_state);
            // update motor state cache
            MOTOR_1_STATE = motor1_new_state;
        }
    }

    // take user input
    readHostControlProfile();

    if (DEBUG_MODE == true)
    {
        cli();
        Serial.print("DIRECTION\t");
        Serial.print(DIRECTION);
        Serial.print("\t");
        Serial.print("THRUST\t");
        Serial.print(THRUST);
        Serial.print("\t");
        Serial.print("ANGLE\t");
        Serial.print(ANGLE);
        Serial.print("\t");
        Serial.print("COMMUTATION_STATE\t");
        Serial.print(MOTOR_1_STATE);
        Serial.print("\t");
        Serial.print("\n");
        sei();
    }
}