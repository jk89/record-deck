#include "./arg_types.h"
#define ENCODER_BUFFER_LENGTH 16
#define ENCODER_BUFFER_MAX_INDEX 15
#define ENCODER_BUFFER_VALUE_MASK 0x3FFF

class Encoder {
    private:
        EncoderPins pins;
    public:
        Encoder(EncoderPins pins) {};
        EncoderPins getPins() {};
        void setup();
        boolean get_sensor_value(uint16_t &value);
        uint32_t get_sensor_value_fast();
};