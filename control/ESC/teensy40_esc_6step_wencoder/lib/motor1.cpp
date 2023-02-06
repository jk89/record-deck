#define PIN_A_IN 2
#define PIN_B_IN 9
#define PIN_C_IN 8
#define PIN_A_SD 1
#define PIN_B_SD 0
#define PIN_C_SD 7 // watchout for ADC sync pin needs to be changed
#define PWM_FREQUENCY 36000
#define FAULT_LED_PIN 13
#define MAX_NUMBER_TRANSTION_IN_REVERSE_PERMITTED 1

int EXPECTED_NEW_STATE[6][2] = {{1, 5}, {2, 0}, {3, 1}, {4, 2}, {5, 3}, {0, 4}}; // IDX 0 {NEXT EXPECTED CW, NEXT EXPECTED CCW}
volatile bool FAULT = false;
volatile int MOTOR_1_STATE = -1;
volatile uint16_t ANGLE = 0;
volatile int WRONG_DIRECTION_CTR = 0;
volatile int ITERATION_CTR = 0;
// import STATE_MAP
#include "calibration_state_map/motor1/commutation_state_locywrlyvnkdzevorzyr.cpp"
/*
// Combined state map looks like this.... CW and CCW over 16384 angular steps
const uint32_t STATE_MAP[2][16384] = {
    CW_STATE_MAP,
    CCW_STATE_MAP,
};
*/
#include "TeensyTimerTool.h"
using namespace TeensyTimerTool;
PeriodicTimer t1(GPT1); // GPT1 module (one 32bit channel per module)

void timing_loop() // t3.begin(LED_ON, 1'000'000);  // Switch LED on every second
{
    cli();
    if (DEBUG_MODE == true && FAULT == false)
    {
        
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
        Serial.print("ITERATION_CTR\t");
        Serial.print(ITERATION_CTR);
        Serial.print("\n");
        ITERATION_CTR = 0;
        
    }
    sei();
}

void init_motor1()
{
    // set pin modes and turn all off
    pinMode(FAULT_LED_PIN, OUTPUT);
    pinMode(PIN_A_IN, OUTPUT);
    pinMode(PIN_B_IN, OUTPUT);
    pinMode(PIN_C_IN, OUTPUT);
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

    // start gpt timer
    t1.begin(timing_loop, 1'000'000);  // Print debugging info on every second
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

void fault(char *reason) // const?
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    init_motor1();                         // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println(reason);                // send fault reason to serial out
    sei();
}

void fault_wrong_direction()
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    init_motor1();                         // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println("Wrong direction");                // send fault reason to serial out
    sei();
}

void fault_skipped_steps()
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    init_motor1();                         // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println("Skipped steps");                // send fault reason to serial out
    sei();
}

void loop_motor1()
{
    // in fault mode sleep to avoid wasting power
    if (FAULT == true)
    {
        delay(10000);
        return;
    }

    if (THRUST != 0)
    {
        ANGLE = as5147p_get_sensor_value_fast(); // get encoder position

        // get relevant state for this encoder position given direction
        int motor1_new_state = STATE_MAP[DIRECTION][ANGLE]; // 16384 in total per direction

        ITERATION_CTR++;

        if (motor1_new_state != MOTOR_1_STATE) // if we have a state change
        {
            if (MOTOR_1_STATE != -1) // validate motor state if not the first time in this loop
            {
                // if we are going in the right direction reset wrong direction counter
                if (motor1_new_state == EXPECTED_NEW_STATE[MOTOR_1_STATE][DIRECTION])
                {
                    WRONG_DIRECTION_CTR = 0;
                }
                // if we are going the wrong direction then inc wrong direction counter and compare to max threshold and fault if needed
                else if (motor1_new_state == EXPECTED_NEW_STATE[MOTOR_1_STATE][REVERSED_DIRECTION])
                {
                    WRONG_DIRECTION_CTR++;
                    // the reason to permit atleast 1 is on the boundary of a state transition there can be noise and so we could go in sequence 0,1,2,1,2,3 by chance
                    if (WRONG_DIRECTION_CTR > MAX_NUMBER_TRANSTION_IN_REVERSE_PERMITTED)
                    {
                        // FAULT WRONG DIRECTION
                        // fault_wrong_direction(); // ("Wrong direction");
                        // return;
                    }
                }
                // we have a totally unexpected state, we either have skipped steps or the encoder is giving us rubbish fault to be safe
                else
                {
                    // FAULT SKIPPED STEPS
                    // fault_skipped_steps(); // fault("Skipped steps");
                    // return;
                }
            }

            // enforce commutation state
            enforce_state_motor1(motor1_new_state);
            // update motor state cache
            MOTOR_1_STATE = motor1_new_state;
        }
    }

    // take user input
    readHostControlProfile();
}