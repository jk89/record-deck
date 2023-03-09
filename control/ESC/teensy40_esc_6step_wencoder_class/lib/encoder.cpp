#include "./encoder.h"

Encoder::Encoder(EncoderPins pins)
{
    this->pins = pins;
}

EncoderPins Encoder::getPins()
{
    return this->pins;
}

void Encoder::setup()
{
    // set pin modes
    pinMode(this->pins.pin_csn, OUTPUT);
    pinMode(this->pins.pin_mosi, OUTPUT);
    pinMode(this->pins.pin_miso, INPUT);
    pinMode(this->pins.pin_sck, OUTPUT);
    // set read angle command bits
    digitalWrite(this->pins.pin_mosi, HIGH); // This can be left high as the command is all ones
};

boolean Encoder::get_sensor_value(uint16_t &value)
{
    // define parity check bit and slave bit buffer
    bool miso_buffer_bit, parity_bit_check = 0;

    value = 0;

    // set CSN low (start a frame) -------------------------------------------
    digitalWriteFast(this->pins.pin_csn, LOW);

    // for each bit in buffer
    for (int buffer_ctr = 0; buffer_ctr < ENCODER_BUFFER_LENGTH; buffer_ctr++)
    {
        // set clock high
        digitalWriteFast(this->pins.pin_sck, HIGH);
        value <<= 1; // bit shift old read value one to left so we can collect a new bit from MISO
        delayNanoseconds(100);
        // set clock low
        digitalWriteFast(this->pins.pin_sck, LOW);
        // now SCK has been pulsed the slave will have written a bit to MISO
        // .... read one bit
        miso_buffer_bit = digitalReadFast(this->pins.pin_miso);
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
    digitalWriteFast(this->pins.pin_csn, HIGH);

    // final parity_bit_check check against first bit
    bool parity_check_result = (parity_bit_check & 1) != (value >> ENCODER_BUFFER_MAX_INDEX);

    // Extract the 14 bits from the 16 bit buffer; which represent the angle step
    value = (value & ENCODER_BUFFER_VALUE_MASK);

    return parity_check_result;
}

uint32_t Encoder::get_sensor_value_fast() {
    // define parity check bit and slave bit buffer
    bool miso_buffer_bit = 0; //, parity_bit_check = 0;

    uint32_t value = 0;
    value <<= 16;

    // set CSN low (start a frame) -------------------------------------------
    digitalWriteFast(this->pins.pin_csn, LOW);

    // ENCODER_BUFFER_LENGTH is 16

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
    value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);

    // ---------
    digitalWriteFast(this->pins.pin_sck, HIGH);
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
    digitalWriteFast(this->pins.pin_sck, LOW);
    miso_buffer_bit = digitalReadFast(this->pins.pin_miso);
    value |= miso_buffer_bit;

    // these last 2 bits are not important for the angle
    digitalWriteFast(this->pins.pin_sck, HIGH);
    digitalWriteFast(this->pins.pin_sck, LOW);
    digitalWriteFast(this->pins.pin_sck, HIGH);
    value <<= 2;
    digitalWriteFast(this->pins.pin_sck, LOW);

    // set CSN high (end frame) -----------------------------------------------
    digitalWriteFast(this->pins.pin_csn, HIGH);

    // Extract the 14 bits from the 16 bit buffer; which represent the angle step
    // ENCODER_BUFFER_VALUE_MASK is 14 1's

    value = (value & ENCODER_BUFFER_VALUE_MASK);

    return value;
}