#include "motor_controller.h"

const char *fault_reason_wrong_direction_during_normal_operation = "Wrong direction during normal operation.. maybe check 3 phase wiring";
const char *fault_reason_wrong_direction_during_startup = "Wrong direction during startup.. maybe check 3 phase wiring";

const char *fault_reason_skipped_steps_during_normal_operation = "Skipped steps during normal operation... maybe check your encoder connection";
const char *fault_reason_skipped_steps_during_startup = "Skipped steps during startup... maybe check your encoder connection";

const char *fault_stall_during_startup = "Startup stall... maybe increment the STARTUP_DUTY or check for motor obstructions";
const char *fault_stall_during_normal_operation = "Stalled... maybe check for motor obstructions or increment your serial controllers minimum thrust value";

MotorWithThrustDirectionProfile::MotorWithThrustDirectionProfile(MotorPins pins, Encoder encoder, MotorArguments args)
{
    // todo validate pins and call validate on encoder/input controller
    this->motor_pins = pins;
    this->encoder = encoder;
    this->input_controller = SerialInputControllerThrustDirectionProfile();

    // todo validate input arguments
    this->state_map = args.state_map;
    this->pwm_frequency = args.pwm_frequency;
    this->max_number_of_transitions_in_reverse_permitted_during_normal_operation = args.max_number_of_transitions_in_reverse_permitted_during_normal_operation;
    this->max_number_of_transitions_in_reverse_permitted_during_startup = args.max_number_of_transitions_in_reverse_permitted_during_startup;
    this->startup_duty = args.startup_duty;
    this->startup_required_number_successful_transitions = args.startup_required_number_successful_transitions;

    // init state and counters

    // state
    this->state = -1;
    this->fault = false;
    this->angle = -1;

    // counters
    this->wrong_direction_normal_ctr = 0;
    this->startup_wrong_direction_ctr = 0;
    this->main_loop_iteration_ctr = 0;
    this->startup_progress_ctr = 0;

    // startup state
    this->startup_last_state = -1;
    this->startup_next_expected_forwards_state = -1;
    this->startup_last_state = -1;
    this->startup_progress_target = args.startup_required_number_successful_transitions;
    this->startup_escape_state_transition_microseconds_estimate = -1;
};

void MotorWithThrustDirectionProfile::take_user_input()
{
    bool new_input = this->input_controller.readProfile();
    if (new_input == true)
    {
        ThrustDirectionProfile profile = this->input_controller.getProfile();
        this->thrust = profile.thrust;
        this->direction = profile.direction;
        this->reversed_direction = this->direction == 0 ? 1 : 0; // stored reverse of direction as well
        this->old_thrust = this->thrust;
    }
}

void MotorWithThrustDirectionProfile::setup()
{
    this->input_controller.setup();
    this->encoder.setup();
};

void MotorWithThrustDirectionProfile::motor_off()
{
    digitalWriteFast(this->motor_pins.pin_a_in, LOW);
    digitalWriteFast(this->motor_pins.pin_b_in, LOW);
    digitalWriteFast(this->motor_pins.pin_c_in, LOW);
    analogWrite(this->motor_pins.pin_a_sd, LOW);
    analogWrite(this->motor_pins.pin_b_sd, LOW);
    analogWrite(this->motor_pins.pin_c_sd, LOW);
    digitalWriteFast(this->motor_pins.pin_a_sd, LOW); // remove these?
    digitalWriteFast(this->motor_pins.pin_b_sd, LOW);
    digitalWriteFast(this->motor_pins.pin_c_sd, LOW);
    asm volatile("dsb");
};

int MotorWithThrustDirectionProfile::get_next_state()
{
    if (this->direction == 0)
    { // cw (dec)
        return (this->state - 1) % 6;
    }
    else
    { // ccw (inc) if (direction == 1)
        return (this->state + 1) % 6;
    }
};

int MotorWithThrustDirectionProfile::get_current_state()
{
    return this->state;
};

int MotorWithThrustDirectionProfile::get_previous_state()
{
    if (this->direction == 0)
    { // cw (inc)
        return (this->state + 1) % 6;
    }
    else
    { // ccw (dec) if (direction == 1)
        return (this->state - 1) % 6;
    }
};

int MotorWithThrustDirectionProfile::get_current_thrust()
{
    return this->thrust;
}

void MotorWithThrustDirectionProfile::enforce_fault(const char *reason)
{
    cli();
    this->fault = true;                                     // indicate fault
    this->thrust = 0;                                       // set thrust to 0
    this->motor_off();                                      // turn everything off
    digitalWriteFast(this->motor_pins.pin_fault_led, HIGH); // turn on fault pin
    Serial.println(reason);                                 // send fault reason to serial out
    sei();
};

void MotorWithThrustDirectionProfile::enforce_state(int thrust_setting)
{
    if (this->state == 0) // 0: A_IN, B_SD
    {
        digitalWriteFast(this->motor_pins.pin_b_in, LOW);
        digitalWriteFast(this->motor_pins.pin_c_in, LOW);
        digitalWriteFast(this->motor_pins.pin_a_sd, LOW);
        digitalWriteFast(this->motor_pins.pin_c_sd, LOW);

        digitalWriteFast(this->motor_pins.pin_a_in, HIGH);
        analogWrite(this->motor_pins.pin_b_sd, thrust_setting);
    }
    else if (this->state == 1) // 1: A_IN, C_SD
    {
        digitalWriteFast(this->motor_pins.pin_b_in, LOW);
        digitalWriteFast(this->motor_pins.pin_c_in, LOW);
        digitalWriteFast(this->motor_pins.pin_a_sd, LOW);
        digitalWriteFast(this->motor_pins.pin_b_sd, LOW);

        digitalWriteFast(this->motor_pins.pin_a_in, HIGH);
        analogWrite(this->motor_pins.pin_c_sd, thrust_setting);
    }
    else if (this->state == 2) // 2: B_IN, C_SD
    {
        digitalWriteFast(this->motor_pins.pin_a_in, LOW);
        digitalWriteFast(this->motor_pins.pin_c_in, LOW);
        digitalWriteFast(this->motor_pins.pin_a_sd, LOW);
        digitalWriteFast(this->motor_pins.pin_b_sd, LOW);

        digitalWriteFast(this->motor_pins.pin_b_in, HIGH);
        analogWrite(this->motor_pins.pin_c_sd, thrust_setting);
    }
    else if (this->state == 3) // 3: B_IN, A_SD
    {
        digitalWriteFast(this->motor_pins.pin_a_in, LOW);
        digitalWriteFast(this->motor_pins.pin_c_in, LOW);
        digitalWriteFast(this->motor_pins.pin_b_sd, LOW);
        digitalWriteFast(this->motor_pins.pin_c_sd, LOW);

        digitalWriteFast(this->motor_pins.pin_b_in, HIGH);
        analogWrite(this->motor_pins.pin_a_sd, thrust_setting);
    }
    else if (this->state == 4) // 4: C_IN, A_SD
    {
        digitalWriteFast(this->motor_pins.pin_a_in, LOW);
        digitalWriteFast(this->motor_pins.pin_b_in, LOW);
        digitalWriteFast(this->motor_pins.pin_b_sd, LOW);
        digitalWriteFast(this->motor_pins.pin_c_sd, LOW);

        digitalWriteFast(this->motor_pins.pin_c_in, HIGH);
        analogWrite(this->motor_pins.pin_a_sd, thrust_setting);
    }
    else if (this->state == 5) // 5: C_IN, B_SD
    {
        digitalWriteFast(this->motor_pins.pin_a_in, LOW);
        digitalWriteFast(this->motor_pins.pin_b_in, LOW);
        digitalWriteFast(this->motor_pins.pin_a_sd, LOW);
        digitalWriteFast(this->motor_pins.pin_c_sd, LOW);

        digitalWriteFast(this->motor_pins.pin_c_in, HIGH);
        analogWrite(this->motor_pins.pin_b_sd, thrust_setting);
    }
    asm volatile("dsb");
};

void MotorWithThrustDirectionProfile::loop()
{
    // in fault mode sleep to avoid wasting power
    if (this->fault == true)
    {
        delay(10000);
        return;
    }

    if (this->thrust != 0 && this->old_thrust != 0)
    {
        delayNanoseconds(90); // delay needed or the encoder creates lots of false values (e.g. 0, 4, 512) noise!
        this->angle = this->encoder.get_sensor_value_fast();

        // get relevant state for this encoder position given direction
        int motor1_new_state = (*this->state_map)[this->direction][this->angle]; // 16384 in total per direction

        this->main_loop_iteration_ctr++;

        if (motor1_new_state != this->state) // if we have a state change
        {
            if (this->state != -1) // validate motor state if not the first time in this loop
            {
                // if we are going in the right direction reset wrong direction counter
                if (motor1_new_state == this->next_expected_state[this->state][this->direction])
                {
                    this->wrong_direction_normal_ctr = 0;
                }
                // if we are going the wrong direction then inc wrong direction counter and compare to max threshold and fault if needed
                else if (motor1_new_state == this->next_expected_state[this->state][this->reversed_direction])
                {
                    this->wrong_direction_normal_ctr++;
                    // the reason to permit atleast 1 is on the boundary of a state transition there can be noise and so we could go in sequence 0,1,2,1,2,3 by chance
                    if (this->wrong_direction_normal_ctr > this->max_number_of_transitions_in_reverse_permitted_during_normal_operation)
                    {
                        this->enforce_fault(fault_reason_wrong_direction_during_normal_operation); // ("Wrong direction");
                        return;
                    }
                }
                // we have a totally unexpected state, we either have skipped steps or the encoder is giving us rubbish fault to be safe
                else
                {
                    this->enforce_fault(fault_reason_skipped_steps_during_normal_operation); // fault("Skipped steps");
                    return;
                }
            }

            // enforce commutation state
            this->state = motor1_new_state;
            this->enforce_state(this->get_current_thrust());
            this->micros_since_last_transition = 0;
            // update motor state cache
        }
        else
        { // motor1_new_state == this->state
            // check for stall
            // todo make this better! no need for cast we should be here if (STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE > 0)
            // should save STARTUP_ESCAPE_STATE_TRANSITION_INTERVAL_MICROSECONDS_ESTIMATE as an unsigned int then this is quick
            if ((this->startup_escape_state_transition_microseconds_estimate > 0) && ((int) this->micros_since_last_transition > this->startup_escape_state_transition_microseconds_estimate))
            {
                // fault stall
                this->enforce_fault(fault_stall_during_normal_operation); // should emit the duty and threshold to serial
                return;
            }
        }
    }
    else if (this->old_thrust == 0 && this->thrust != 0) // if we were off and are now on ... startup routine
    { // What about STALL?
        // startup
        int startup_exit_condition = this->startup_procedure();
        if (startup_exit_condition > 0)
        {
            this->startup_escape_state_transition_microseconds_estimate = startup_exit_condition;
        }
        else if (startup_exit_condition == -1)
        {
            this->enforce_fault(fault_reason_wrong_direction_during_startup);
            return;
        }
        else if (startup_exit_condition == -2)
        {
            this->enforce_fault(fault_reason_skipped_steps_during_startup);
            return;
        }
        else if (startup_exit_condition == -3)
        {
            this->enforce_fault(fault_stall_during_startup); // consider uping pwm duty in a loop until we find a minimum
            return;
        }
    }
    else if (this->thrust == 0)
    {
        this->motor_off();
        return;
    }
};

int MotorWithThrustDirectionProfile::startup_procedure()
{
    this->startup_progress_ctr = 0;
    this->startup_wrong_direction_ctr = 0;

    // read initial state
    uint16_t angle = this->encoder.get_sensor_value_fast();
    this->angle = angle;
    this->startup_last_state = *(this->state_map)[this->direction][angle];
    this->startup_next_expected_forwards_state = this->next_expected_state[this->startup_last_state][this->direction];
    this->startup_next_expected_backwards_state = this->next_expected_state[this->startup_last_state][this->reversed_direction];

    this->state = this->startup_last_state;
    int forced_state = this->get_previous_state();

    // do a linear chirp to force initial motor commutation
    int i = 5000;
    while (i > 20)
    {
        // force commutation forwards
        forced_state = this->get_next_state();
        this->state = forced_state;
        enforce_state(this->startup_duty);

        // wait a bit
        delayMicroseconds(i);

        // find current state
        angle = this->encoder.get_sensor_value_fast();

        int motor1_state = (*this->state_map)[this->direction][angle];
        int motor1_next_expected_state = this->next_expected_state[motor1_state][this->direction];
        int motor1_next_backwards_expected_state = this->next_expected_state[motor1_state][this->reversed_direction];

        // compare new and old states

        if (motor1_state == this->startup_last_state)
        {
            // nothing has changed
        }
        else if (motor1_state == this->startup_next_expected_forwards_state)
        {
            // we have made a transition in the right direction
            this->startup_progress_ctr++;
            this->startup_wrong_direction_ctr = 0;
            if (this->startup_progress_ctr >= this->startup_progress_target)
            {
                this->micros_since_last_transition = 0;
                return i; // escape startup routine
            }
        }
        else if (motor1_state == this->startup_next_expected_backwards_state)
        {
            // we went the wrong way!
            this->startup_wrong_direction_ctr++;
            this->startup_progress_ctr = 0;

            if (this->startup_wrong_direction_ctr > this->max_number_of_transitions_in_reverse_permitted_during_startup) // could relax this constraint a bit
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

        this->startup_last_state = motor1_state;
        this->startup_next_expected_forwards_state = motor1_next_expected_state;
        this->startup_next_expected_backwards_state = motor1_next_backwards_expected_state;

        i = i - 20; // decrement delay time (increase frequency)
    }

    return -3; // fault did not make required progress
};