// pins

#define PIN_CSN 10
#define PIN_SCK 13
#define PIN_MISO 12
#define PIN_MOSI 11
#define ENCODER_BUFFER 16
#define ENCODER_BUFFER_MAX_INDEX 15
#define ENCODER_BUFFER_VALUE_MASK       (0x3FFF)

void as5147p_setup()
{
    pinMode(PIN_CSN, OUTPUT);
    pinMode(PIN_MOSI, OUTPUT);
    pinMode(PIN_MISO, INPUT);
    pinMode(PIN_SCK, OUTPUT);
    digitalWrite(PIN_MOSI, HIGH); // This can be left high as the command is 0xFFFF (all ones)
}

boolean as5147p_get_raw_sensor_value(uint16_t &value)
{
    // set value to zero
    value = 0;
    // define parity and bit read buffer
    uint8_t slave_read_bit, parity = 0;

    // for each data frame

    // set CSN low (start a frame)
    digitalWriteFast(PIN_CSN, LOW);

    // for each bit in buffer

    for (int buffer_ctr = 0; buffer_ctr < ENCODER_BUFFER; buffer_ctr++)
    {
        // set clock high
        digitalWriteFast(PIN_SCK, HIGH);
        value <<= 1;
        // delayMicroseconds(1); // 1Mhz
        delayNanoseconds(3); // 10 15 20 stable
        // set clock low
        digitalWriteFast(PIN_SCK, LOW);
        // now SCK has been pulsed the slave will have written a bit to MISO
        slave_read_bit = digitalReadFast(PIN_MISO);
        value |= slave_read_bit;

        if (buffer_ctr > 0) {
            parity += slave_read_bit;
        }
    }

    

    // set CSN high (end frame)
    digitalWriteFast(PIN_CSN, HIGH);

    // final parity check
    bool final_parity =  ( (parity&1) != (value>>ENCODER_BUFFER_MAX_INDEX) );

    // get the final result

    value = (value & ENCODER_BUFFER_VALUE_MASK);

    return final_parity;
}