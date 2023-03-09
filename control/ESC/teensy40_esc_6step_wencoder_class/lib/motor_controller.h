#include "./types.h"
#include "./encoder.h"
#include "./coms.h"

class MotorWithThrustDirectionProfile
{
private:
    const int next_expected_state[6][2] = {{5, 1}, {0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 0}};
    int pwm_frequency;
    MotorPins motor_pins;
    Encoder encoder;
    SerialInputControllerThrustDirectionProfile input_controller;
    bool fault;
    int state;
    int angle;
    int thrust;
    int direction;
    bool reversed_direction;
    int old_thrust;

    int wrong_direction_normal_ctr;
    int main_loop_iteration_ctr;

    uint32_t (*state_map)[2][ENCODER_DEVISIONS];

    int startup_last_state;
    int startup_next_expected_forwards_state;
    int startup_next_expected_backwards_state;
    int startup_progress_ctr;
    int startup_progress_target;
    int startup_duty;
    int startup_escape_state_transition_microseconds_estimate;
    int startup_wrong_direction_ctr;

    elapsedMicros micros_since_last_transition;

    int max_number_of_transitions_in_reverse_permitted_during_normal_operation;
    int max_number_of_transitions_in_reverse_permitted_during_startup;
    int startup_duty;
    int startup_required_number_successful_transitions;
    void enforce_fault(const char *reason);
    int get_current_thrust();
    void enforce_state(int thrust);
    int startup_procedure(){};

public:
    MotorWithThrustDirectionProfile(MotorPins pins, Encoder enc, MotorArguments args);
    void motor_off();
    int get_next_state();
    int get_current_state();
    int get_previous_state();

    void setup();
    void loop();
    void take_user_input(){};
};