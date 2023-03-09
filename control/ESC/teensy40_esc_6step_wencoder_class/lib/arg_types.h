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

struct MotorArguments
{
    int max_number_of_transitions_in_reverse_permitted_during_normal_operation;
    int max_number_of_transitions_in_reverse_permitted_during_startup;
    int startup_duty;
};

struct EncoderPins
{
    int pin_csn;
    int pin_sck;
    int pin_miso;
    int pin_mosi;
};