#include "./types.h"

class Encoder {
    private:
        EncoderPins pins;
    public:
        Encoder(EncoderPins pins);
        EncoderPins getPins();
        void setup();
        boolean get_sensor_value(uint16_t &value);
        uint32_t get_sensor_value_fast();
};