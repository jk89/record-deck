#include "./arg_types.h"
#include "./encoder.cpp"
#define ENCODER_BUFFER_LENGTH 16
#define ENCODER_BUFFER_MAX_INDEX 15
#define ENCODER_BUFFER_VALUE_MASK 0x3FFF

struct SensorValues
{
    uint32_t enc1_val;
    uint32_t enc2_val;
}

class DualEncoder
{
private:
    EncoderPins pins_enc1;
    EncoderPins pins_enc2;
    Encoder enc1;
    Encoder enc2;

public:
    DualEncoder(Encoder enc1, Encoder enc2);
    void setup(){};
    SensorValues get_sensors_values(){};
};