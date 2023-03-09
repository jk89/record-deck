#include "./types.h"
#include "./encoder.h"

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