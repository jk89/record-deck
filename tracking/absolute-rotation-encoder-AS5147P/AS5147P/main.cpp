// pins

#define PIN_CSN 10
#define PIN_SCK 13
#define PIN_MISO 12
#define PIN_MOSI 11
#define ENCODER_BUFFER_LENGTH 16
#define ENCODER_BUFFER_MAX_INDEX 15
#define ENCODER_BUFFER_VALUE_MASK 0x3FFF

void as5147p_setup()
{
    // set pin modes
    pinMode(PIN_CSN, OUTPUT);
    pinMode(PIN_MOSI, OUTPUT);
    pinMode(PIN_MISO, INPUT);
    pinMode(PIN_SCK, OUTPUT);
    // set read angle command bits
    digitalWrite(PIN_MOSI, HIGH); // This can be left high as the command is all ones
}

boolean as5147p_get_sensor_value(uint16_t &value)
{
    // define parity check bit and slave bit buffer
    bool miso_buffer_bit, parity_bit_check = 0;

    value = 0;

    // set CSN low (start a frame) -------------------------------------------
    digitalWriteFast(PIN_CSN, LOW);

    // for each bit in buffer
    for (int buffer_ctr = 0; buffer_ctr < ENCODER_BUFFER_LENGTH; buffer_ctr++)
    {
        // set clock high
        digitalWriteFast(PIN_SCK, HIGH);
        value <<= 1; // bit shift old read value one to left so we can collect a new bit from MISO
        delayNanoseconds(3); // Without this parity_bit_check checks start to fail
        // set clock low
        digitalWriteFast(PIN_SCK, LOW);
        // now SCK has been pulsed the slave will have written a bit to MISO
        // .... read one bit
        miso_buffer_bit = digitalReadFast(PIN_MISO);
        // append the latest bit to value
        value |= miso_buffer_bit;

        // sum parity
        if (buffer_ctr > 0) {
            parity_bit_check += miso_buffer_bit;
        }
    }

    // set CSN high (end frame) -----------------------------------------------
    digitalWriteFast(PIN_CSN, HIGH);

    // final parity_bit_check check against first bit
    bool parity_check_result = (parity_bit_check & 1) != (value >> ENCODER_BUFFER_MAX_INDEX);

    // Extract the 14 bits from the 16 bit buffer; which represent the angle step
    value = (value & ENCODER_BUFFER_VALUE_MASK);

    return parity_check_result;
}