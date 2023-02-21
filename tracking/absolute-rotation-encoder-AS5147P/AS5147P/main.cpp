// pins

#define PIN_CSN 10
#define PIN_SCK 22
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
        delayNanoseconds(100);
        // set clock low
        digitalWriteFast(PIN_SCK, LOW);
        // now SCK has been pulsed the slave will have written a bit to MISO
        // .... read one bit
        miso_buffer_bit = digitalReadFast(PIN_MISO);
        // append the latest bit to value
        value |= miso_buffer_bit;

        // sum parity
        if (buffer_ctr > 0)
        {
            parity_bit_check += miso_buffer_bit;
        }
    }
    delayNanoseconds(10);

    // set CSN high (end frame) -----------------------------------------------
    digitalWriteFast(PIN_CSN, HIGH);

    // final parity_bit_check check against first bit
    bool parity_check_result = (parity_bit_check & 1) != (value >> ENCODER_BUFFER_MAX_INDEX);

    // Extract the 14 bits from the 16 bit buffer; which represent the angle step
    value = (value & ENCODER_BUFFER_VALUE_MASK);

    return parity_check_result;
}

uint32_t as5147p_get_sensor_value_fast()
{
    // define parity check bit and slave bit buffer
    bool miso_buffer_bit = 0; //, parity_bit_check = 0;

    uint32_t value = 0;
    value <<= 16;

    // set CSN low (start a frame) -------------------------------------------
    digitalWriteFast(PIN_CSN, LOW);

    // ENCODER_BUFFER_LENGTH is 16

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);

    // ---------
    digitalWriteFast(PIN_SCK, HIGH);
    value |= miso_buffer_bit;
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(PIN_SCK, LOW);
    miso_buffer_bit = digitalReadFast(PIN_MISO);
    value |= miso_buffer_bit;

    // these last 2 bits are not important for the angle
    digitalWriteFast(PIN_SCK, HIGH);
    digitalWriteFast(PIN_SCK, LOW);
    digitalWriteFast(PIN_SCK, HIGH);
    value <<= 2;
    digitalWriteFast(PIN_SCK, LOW);

    // set CSN high (end frame) -----------------------------------------------
    digitalWriteFast(PIN_CSN, HIGH);

    // final parity_bit_check check against first bit
    // bool parity_check_result = (parity_bit_check & 1) != (value >> ENCODER_BUFFER_MAX_INDEX);

    // Extract the 14 bits from the 16 bit buffer; which represent the angle step

    // ENCODER_BUFFER_VALUE_MASK is 14 1's

    value = (value & ENCODER_BUFFER_VALUE_MASK);

    return value; // parity_check_result;
}