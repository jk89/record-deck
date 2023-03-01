#define PIN_A_IN 2
#define PIN_B_IN 9
#define PIN_C_IN 8
#define PIN_A_SD 1
#define PIN_B_SD 0
#define PIN_C_SD 7          // watchout for ADC sync pin needs to be changed
#define PWM_FREQUENCY 36000 // 40000 // 36000// 32000
#define FAULT_LED_PIN 13
#define MAX_NUMBER_TRANSTION_IN_REVERSE_PERMITTED 1

// int EXPECTED_NEW_STATE[6][2] = {{1, 5}, {2, 0}, {3, 1}, {4, 2}, {5, 3}, {0, 4}}; // IDX 0 {NEXT EXPECTED CW, NEXT EXPECTED CCW}
int EXPECTED_NEW_STATE[6][2] = {{5, 1}, {0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 0}}; // IDX 0 {NEXT EXPECTED CW, NEXT EXPECTED CCW}

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

/*
    FlexPWM1.0	1, 44, 45	4.482 kHz this
    FlexPWM1.1	0, 42, 43	4.482 kHz this
    FlexPWM1.2	24, 46, 47	4.482 kHz
    FlexPWM1.3	7, 8, 25	4.482 kHz this
*/

/*

INIT_SEL
Initialization Control Select
These read/write bits control the source of the INIT signal which goes to the counter.
0    00b - Local sync (PWM_X) causes initialization.
1    01b - Master reload from submodule 0 causes initialization. This setting should not be used in
    submodule 0 as it will force the INIT signal to logic 0. The submodule counter will only reinitialize
    when a master reload occurs.
2    10b - Master sync from submodule 0 causes initialization. This setting should not be used in
    submodule 0 as it will force the INIT signal to logic 0
3    11b - EXT_SYNC causes initialization.

*/

/*

Clock Source Select
These read/write bits determine the source of the clock signal for this submodule.
0    00b - The IPBus clock is used as the clock for the local prescaler and counter.
1    01b - EXT_CLK is used as the clock for the local prescaler and counter.
2    10b - Submodule 0’s clock (AUX_CLK) is used as the source clock for the local prescaler and
    counter. This setting should not be used in submodule 0 as it will force the clock to logic 0.
3    11b - reserved

*/
void init_pwm1_again() // from jk acmp project
{
    return; // NOTE have changed init_sel(0) to init_sel(2) DANGER
    // https://www.pjrc.com/teensy/IMXRT1060RM_rev3.pdf 55.8.4.3 Fields
    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY);
    // FLEXPWM1_SM0TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 4);

    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_CLDOK(0x0F); //  Clear Load Okay LDOK(SM) -> no reload of PWM settings
    // FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(0); // A & B independant | sm0 chosen as clock (SHOULD BE 2 SM0 !)
    FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(2); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_LDOK(0x0F);                                                           // Load Okay LDOK(SM) -> reload setting again
    // FLEXPWM1_SM1TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 4);

    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_CLDOK(0x0F); //  Clear Load Okay LDOK(SM) -> no reload of PWM settings
    // FLEXPWM1_SM3CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(0); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_SM3CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(2); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_LDOK(0x0F);                                                           // Load Okay LDOK(SM) -> reload setting again
    // FLEXPWM1_SM3TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 4);
    asm volatile("dsb");
}

void init_pwm1_danger()
{
    // https://github.com/ElwinBoots/Teensy_DualMotorBoard_V1/blob/master/Teensy_DualMotorBoard_V1.ino
    // https://www.rapidtables.com/convert/number/decimal-to-binary.html
    // https://www.pjrc.com/teensy/IMXRT1060RM_rev3.pdf  55.8.4.3 Fields

    // warning this killed the power circuit!
    return;

    /*
    original
    FLEXPWM1_SM0CTRL2 = FLEXPWM_SMCTRL2_INDEP; //Enable Independent pair, but disable Debug Enable and WAIT Enable. When set to one, the PWM will continue to run while the chip is in debug/WAIT mode.
    FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP; //Enable Independent pair, but disable Debug Enable and WAIT Enable. When set to one, the PWM will continue to run while the chip is in debug/WAIT mode.
    FLEXPWM1_SM2CTRL2 = FLEXPWM_SMCTRL2_INDEP; //Enable Independent pair, but disable Debug Enable and WAIT Enable. When set to one, the PWM will continue to run while the chip is in debug/WAIT mode.

    FLEXPWM1_SM0CTRL2 |= FLEXPWM_SMCTRL2_FRCEN;
    FLEXPWM1_SM1CTRL2 |= FLEXPWM_SMCTRL2_INIT_SEL(2); // Master sync from submodule 0 causes initialization.
    FLEXPWM1_SM2CTRL2 |= FLEXPWM_SMCTRL2_INIT_SEL(2); //  Master sync from submodule 0 causes initialization.

    FLEXPWM1_SM0CTRL2 |= FLEXPWM_SMCTRL2_FORCE; // Force FlexPWM2
    */

    FLEXPWM1_SM0CTRL2 = FLEXPWM_SMCTRL2_INDEP; // Enable Independent pair, but disable Debug Enable and WAIT Enable. When set to one, the PWM will continue to run while the chip is in debug/WAIT mode.
    FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP; // Enable Independent pair, but disable Debug Enable and WAIT Enable. When set to one, the PWM will continue to run while the chip is in debug/WAIT mode.
    FLEXPWM1_SM3CTRL2 = FLEXPWM_SMCTRL2_INDEP; // Enable Independent pair, but disable Debug Enable and WAIT Enable. When set to one, the PWM will continue to run while the chip is in debug/WAIT mode.

    // FLEXPWM1_SM0CTRL2 |= FLEXPWM_SMCTRL2_FRCEN; DISABLED
    FLEXPWM1_SM1CTRL2 |= FLEXPWM_SMCTRL2_INIT_SEL(2); // Master sync from submodule 0 causes initialization.
    FLEXPWM1_SM3CTRL2 |= FLEXPWM_SMCTRL2_INIT_SEL(2); //  Master sync from submodule 0 causes initialization.

    // FLEXPWM1_SM0CTRL2 |= FLEXPWM_SMCTRL2_FORCE; // Force FlexPWM2 DISABLED
}

void motor1_off()
{
    digitalWriteFast(PIN_A_IN, LOW);
    digitalWriteFast(PIN_B_IN, LOW);
    digitalWriteFast(PIN_C_IN, LOW);
    analogWrite(PIN_A_SD, LOW);
    analogWrite(PIN_B_SD, LOW);
    analogWrite(PIN_C_SD, LOW);
    digitalWriteFast(PIN_A_SD, LOW); // remove these?
    digitalWriteFast(PIN_B_SD, LOW);
    digitalWriteFast(PIN_C_SD, LOW);
    asm volatile("dsb");
}

void init_motor1()
{
    cli();

    // set pin modes and turn all off
    pinMode(FAULT_LED_PIN, OUTPUT);
    pinMode(PIN_A_IN, OUTPUT);
    pinMode(PIN_B_IN, OUTPUT);
    pinMode(PIN_C_IN, OUTPUT);
    pinMode(PIN_A_SD, OUTPUT);
    pinMode(PIN_B_SD, OUTPUT);
    pinMode(PIN_C_SD, OUTPUT);

    analogWriteRes(8);

    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY); // also contained withing init_pwm1_again

    // init_pwm1_again(); !careful this could kill hardware // blocked with a first line return statement

    motor1_off();
    digitalWriteFast(FAULT_LED_PIN, LOW); // FAULT LED OFF

    // start gpt timer
    t1.begin(timing_loop, 1'000'000); // Print debugging info on every second

    asm volatile("dsb");

    sei();
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

void enforce_state_motor1(int state, int thrust)
{
    // return;
    if (state == 0) // 0: A_IN, B_SD
    {
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_A_IN, HIGH);
        analogWrite(PIN_B_SD, thrust);
    }
    else if (state == 1) // 1: A_IN, C_SD
    {
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_B_SD, LOW);

        digitalWriteFast(PIN_A_IN, HIGH);
        analogWrite(PIN_C_SD, thrust);
    }
    else if (state == 2) // 2: B_IN, C_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_B_SD, LOW);

        digitalWriteFast(PIN_B_IN, HIGH);
        analogWrite(PIN_C_SD, thrust);
    }
    else if (state == 3) // 3: B_IN, A_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_B_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_B_IN, HIGH);
        analogWrite(PIN_A_SD, thrust);
    }
    else if (state == 4) // 4: C_IN, A_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_B_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_C_IN, HIGH);
        analogWrite(PIN_A_SD, thrust);
    }
    else if (state == 5) // 5: C_IN, B_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_C_IN, HIGH);
        analogWrite(PIN_B_SD, thrust);
    }
    asm volatile("dsb");
}

void fault(char *reason) // const?
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    motor1_off();                          // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println(reason);                // send fault reason to serial out
    sei();
}

void fault_wrong_direction()
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    motor1_off();                          // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println("Wrong direction");     // send fault reason to serial out
    sei();
}

void fault_skipped_steps()
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    motor1_off();                          // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println("Skipped steps");       // send fault reason to serial out
    sei();
}

void fault_stall()
{
    cli();
    FAULT = true;                          // indicate fault
    THRUST = 0;                            // set thrust to 0
    motor1_off();                          // turn everything off
    digitalWriteFast(FAULT_LED_PIN, HIGH); // turn on fault pin
    Serial.println("Stalled");       // send fault reason to serial out
    sei();
}


// startup procedure
volatile int STARTUP_LAST_STATE = -1;
volatile int STARTUP_LAST_NEXT_EXPECTED_STATE = -1;
volatile int STARTUP_LAST_NEXT_BACKWARDS_EXPECTED_STATE = -1;
volatile int STARTUP_PROGRESS_CTR = 0;
int STARTUP_PROGRESS_TARGET = 6;
int STARTUP_DUTY = 10;
int STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE = -1;
elapsedMicros MICROS_SINCE_LAST_TRANSITION;

// int EXPECTED_NEW_STATE[6][2] = {{5, 1}, {0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 0}}; // IDX 0 {NEXT EXPECTED CW, NEXT EXPECTED CCW}
// 0 is CW (0->5->4->3->2->1->0) -- % 6
// 1 is CCW (1->2->3->4->5->0->1) ++ % 6

int next_state(int current_state, int direction)
{
    if (direction == 0)
    { // cw (dec)
        return (current_state - 1) % 6;
    }
    else
    { // ccw (inc) if (direction == 1)
        return (current_state + 1) % 6;
    }
}

int prev_state(int current_state, int direction)
{
    if (direction == 0)
    { // cw (inc)
        return (current_state + 1) % 6;
    }
    else
    { // ccw (dec) if (direction == 1)
        return (current_state - 1) % 6;
    }
}

// this routine is here to overcome the initial stationary rotor problem.
// swap through all states in order (respecting direction) and do this with increasing frequency
// motor should be perturbed and 'caught' by these rotating magnetic fields and start synchronising.
// when the motor has made enough consecutive progress in the right direction then we can escape (default 6 steps or a complete electrical cycle (6/((POLES/2)*6))*100% e.g. 14.29% of a complete rotation for a 14 pole motor
// if the motor spins the wrong way or skips steps due to violent motion we can fault.

int motor1_startup()
{
    STARTUP_PROGRESS_CTR = 0;
    WRONG_DIRECTION_CTR = 0;

    // read initial state
    uint16_t angle = as5147p_get_sensor_value_fast();
    STARTUP_LAST_STATE = STATE_MAP[DIRECTION][angle];
    STARTUP_LAST_NEXT_EXPECTED_STATE = EXPECTED_NEW_STATE[STARTUP_LAST_STATE][DIRECTION];
    STARTUP_LAST_NEXT_BACKWARDS_EXPECTED_STATE = EXPECTED_NEW_STATE[STARTUP_LAST_STATE][REVERSED_DIRECTION];

    int forced_state = prev_state(STARTUP_LAST_STATE, DIRECTION);

    // do a linear chirp to force initial motor commutation
    int i = 5000;
    while (i > 20)
    {
        // force commutation forwards
        forced_state = next_state(forced_state, DIRECTION);
        enforce_state_motor1(forced_state, STARTUP_DUTY);

        // wait a bit
        delayMicroseconds(i);

        // find current state
        angle = as5147p_get_sensor_value_fast();
        int motor1_state = STATE_MAP[DIRECTION][angle];
        int motor1_next_expected_state = EXPECTED_NEW_STATE[motor1_state][DIRECTION];
        int motor1_next_backwards_expected_state = EXPECTED_NEW_STATE[motor1_state][REVERSED_DIRECTION];

        // compare new and old states

        if (motor1_state == STARTUP_LAST_STATE)
        {
            // nothing has changed
        }
        else if (motor1_state == STARTUP_LAST_NEXT_EXPECTED_STATE)
        {
            // we have made a transition in the right direction
            STARTUP_PROGRESS_CTR++;
            if (STARTUP_PROGRESS_CTR >= STARTUP_PROGRESS_TARGET)
            {
                MICROS_SINCE_LAST_TRANSITION = 0;
                return i; // escape startup routine
            }
        }
        else if (motor1_state == STARTUP_LAST_NEXT_BACKWARDS_EXPECTED_STATE)
        {
            // we went the wrong way!
            WRONG_DIRECTION_CTR++;
            STARTUP_PROGRESS_CTR = 0;

            if (WRONG_DIRECTION_CTR > MAX_NUMBER_TRANSTION_IN_REVERSE_PERMITTED) // could relax this constraint a bit
            {
                return -1;
            }
        }
        else
        {
            // bad transition
            return -2;
        }

        // if we got this far then either we have made no progress yet or we have made some progress (no escape condition yet) but no failure states yet

        STARTUP_LAST_STATE = motor1_state;
        STARTUP_LAST_NEXT_EXPECTED_STATE = motor1_next_expected_state;
        STARTUP_LAST_NEXT_BACKWARDS_EXPECTED_STATE = motor1_next_backwards_expected_state;
        i = i - 20; // decrement delay time (increase frequency)
    }

    return -3; // fault did not make required progress
}

void loop_motor1()
{
    // in fault mode sleep to avoid wasting power
    if (FAULT == true)
    {
        delay(10000);
        return;
    }

    if (OLD_THRUST == 0 && THRUST != 0) { // What about STALL?
        // startup
        int startup_exit_condition = motor1_startup();
        if (startup_exit_condition > 0 ) {
            STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE = startup_exit_condition;
        }
        else if (startup_exit_condition == -1 ) {
            fault_wrong_direction();
            return;
        }
        else if (startup_exit_condition == -2) {
            fault_skipped_steps();
            return;
        }
        else if (startup_exit_condition == -3) {
            fault_stall(); // consider uping pwm duty in a loop until we find a minimum
            return;
        }
    }
    else if (THRUST != 0)
    {
        delayNanoseconds(90); // delay needed or the encoder creates lots of false values (e.g. 0, 4, 512) noise!
        ANGLE = as5147p_get_sensor_value_fast();

        // get relevant state for this encoder position given direction
        int motor1_new_state = STATE_MAP[DIRECTION][ANGLE]; // 16384 in total per direction

        ITERATION_CTR++;

        if (motor1_new_state != MOTOR_1_STATE) // if we have a state change // && ANGLE != 0
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
                        cli();
                        Serial.print("fault wrong direction\t");
                        Serial.print("angle\t");
                        Serial.print(ANGLE);
                        Serial.print("\told motor state \t");
                        Serial.print(MOTOR_1_STATE);
                        Serial.print("\tmotor1_new_state\t");
                        Serial.print(motor1_new_state);
                        Serial.print("\tEXPECTED_NEW_STATE[MOTOR_1_STATE][REVERSED_DIRECTION]\t");
                        Serial.print(EXPECTED_NEW_STATE[MOTOR_1_STATE][REVERSED_DIRECTION]);
                        Serial.print("\n");
                        sei();

                        fault_wrong_direction(); // ("Wrong direction");
                        return;
                    }
                }
                // we have a totally unexpected state, we either have skipped steps or the encoder is giving us rubbish fault to be safe
                else
                {
                    // FAULT SKIPPED STEPS
                    cli();
                    Serial.print("fault skip\t");
                    Serial.print("angle\t");
                    Serial.print(ANGLE);
                    Serial.print("\told motor state \t");
                    Serial.print(MOTOR_1_STATE);
                    Serial.print("\tmotor1_new_state\t");
                    Serial.print(motor1_new_state);
                    Serial.print("\tEXPECTED_NEW_STATE[MOTOR_1_STATE][DIRECTION]\t");
                    Serial.print(EXPECTED_NEW_STATE[MOTOR_1_STATE][DIRECTION]);
                    Serial.print("\n");
                    sei();

                    fault_skipped_steps(); // fault("Skipped steps");
                    return;
                }
            }

            // enforce commutation state
            enforce_state_motor1(motor1_new_state, THRUST);
            MICROS_SINCE_LAST_TRANSITION = 0;
            // update motor state cache
            MOTOR_1_STATE = motor1_new_state;
        }
        else { // motor1_new_state == MOTOR_1_STATE
            // check for stall
            // todo make this better! no need for cast we should be here if (STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE > 0)
            // should save STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE as an unsigned int then this is quick
            if ((STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE > 0) && ((int) MICROS_SINCE_LAST_TRANSITION > STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE)) {
                // fault stall
                fault_stall(); // should emit the duty and threshold to serial
            }
        }
    }
}
