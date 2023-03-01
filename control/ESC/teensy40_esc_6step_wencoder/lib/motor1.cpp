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

void init_pwm1_again() // from jk acmp project
{
    return; // NOTE have changed init_sel(0) to init_sel(2)
    // https://www.pjrc.com/teensy/IMXRT1060RM_rev3.pdf 55.8.4.3 Fields
    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY);
    // FLEXPWM1_SM0TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 4);

    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_CLDOK(0x0F); //  Clear Load Okay LDOK(SM) -> no reload of PWM settings
    // FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(0); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(2); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_LDOK(0x0F);                                                           // Load Okay LDOK(SM) -> reload setting again
    // FLEXPWM1_SM1TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 4);

    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_CLDOK(0x0F); //  Clear Load Okay LDOK(SM) -> no reload of PWM settings
    // FLEXPWM1_SM3CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(0); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_SM3CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(2); // A & B independant | sm0 chosen as clock (SHOULD BE 2!)
    FLEXPWM1_MCTRL |= FLEXPWM_MCTRL_LDOK(0x0F);                                                           // Load Okay LDOK(SM) -> reload setting again
    // FLEXPWM1_SM3TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 4);
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
    FLEXPWM1_SM1CTRL2 = FLEXPWM_SMCTRL2_INDEP | FLEXPWM_SMCTRL2_CLK_SEL(2) | FLEXPWM_SMCTRL2_INIT_SEL(0); //A & B independant | sm0 chosen as clock
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

    digitalWriteFast(PIN_A_SD, LOW);
    digitalWriteFast(PIN_B_SD, LOW);
    digitalWriteFast(PIN_C_SD, LOW);

    asm volatile("dsb");
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

    analogWriteRes(8);

    analogWriteFrequency(PIN_A_SD, PWM_FREQUENCY);

    // init_pwm1_again(); !careful this could kill hardware

    motor1_off();

    digitalWriteFast(FAULT_LED_PIN, LOW);

    // start gpt timer
    t1.begin(timing_loop, 1'000'000); // Print debugging info on every second

    // return;
    asm volatile("dsb");
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
    // return;
    if (state == 0) // 0: A_IN, B_SD
    {
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_A_IN, HIGH);
        analogWrite(PIN_B_SD, THRUST);
    }
    else if (state == 1) // 1: A_IN, C_SD
    {
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_B_SD, LOW);

        digitalWriteFast(PIN_A_IN, HIGH);
        analogWrite(PIN_C_SD, THRUST);
    }
    else if (state == 2) // 2: B_IN, C_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_B_SD, LOW);

        digitalWriteFast(PIN_B_IN, HIGH);
        analogWrite(PIN_C_SD, THRUST);
    }
    else if (state == 3) // 3: B_IN, A_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_C_IN, LOW);
        digitalWriteFast(PIN_B_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_B_IN, HIGH);
        analogWrite(PIN_A_SD, THRUST);
    }
    else if (state == 4) // 4: C_IN, A_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_B_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_C_IN, HIGH);
        analogWrite(PIN_A_SD, THRUST);
    }
    else if (state == 5) // 5: C_IN, B_SD
    {
        digitalWriteFast(PIN_A_IN, LOW);
        digitalWriteFast(PIN_B_IN, LOW);
        digitalWriteFast(PIN_A_SD, LOW);
        digitalWriteFast(PIN_C_SD, LOW);

        digitalWriteFast(PIN_C_IN, HIGH);
        analogWrite(PIN_B_SD, THRUST);
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
        delayNanoseconds(90);
        uint16_t angle = as5147p_get_sensor_value_fast();
        bool par = false; // as5147p_get_sensor_value(angle);
        // ignore special states?? i hate this
        /*if (angle == 0) //  || angle == 512 || angle == 4 || angle == 518
        {
            return;
        }*/
        ANGLE = angle; // get encoder position

        // get relevant state for this encoder position given direction
        int motor1_new_state = STATE_MAP[DIRECTION][ANGLE]; // 16384 in total per direction

        ITERATION_CTR++;

        /*Serial.print("MOTOR_1_STATE\t");
        Serial.print(MOTOR_1_STATE);
        Serial.print("\tmotor1_new_state");
        Serial.println(motor1_new_state);*/

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
                        Serial.print("\tparity\t");
                        Serial.print(par);
                        Serial.print("\told motor state \t");
                        Serial.print(MOTOR_1_STATE);
                        Serial.print("\tmotor1_new_state\t");
                        Serial.print(motor1_new_state);
                        Serial.print("\tEXPECTED_NEW_STATE[MOTOR_1_STATE][REVERSED_DIRECTION]\t");
                        Serial.print(EXPECTED_NEW_STATE[MOTOR_1_STATE][REVERSED_DIRECTION]);
                        Serial.print("\n");
                        sei();

                        // fault_wrong_direction(); // ("Wrong direction");
                        // return;
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
                    Serial.print("\tparity\t");
                    Serial.print(par);
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
            enforce_state_motor1(motor1_new_state);
            // update motor state cache
            MOTOR_1_STATE = motor1_new_state;
        }
    }
}