struct MotorPins
{
    int pin_a_in;
    int pin_a_sd;

    int pin_b_in;
    int pin_b_sd;

    int pin_c_in;
    int pin_c_sd;

    int pin_fault_led;
};

const int ENCODER_DEVISIONS = 16384;

struct MotorArguments
{
    int max_number_of_transitions_in_reverse_permitted_during_normal_operation;
    int max_number_of_transitions_in_reverse_permitted_during_startup;
    int startup_duty;
    int pwm_frequency;
    int startup_required_number_successful_transitions;
    uint32_t (*state_map)[2][ENCODER_DEVISIONS];
};

struct EncoderPins
{
    int pin_csn;
    int pin_sck;
    int pin_miso;
    int pin_mosi;
};

struct ThrustDirectionProfile
{
    int thrust;
    bool direction;
};

struct ThrustDirectionPitchRollProfile
{
    int thrust;
    bool direction;
    float pitch;
    float roll;
};