#include "./dual_encoder.h"

DualEncoder::DualEncoder(Encoder enc1, Encoder enc2)
{
    this->enc1 = enc1;
    this->enc2 = enc2;
    this->pins_enc1 = enc1.getPins();
    this->pins_enc2 = enc2.getPins();
}

void DualEncoder::setup()
{
    this->enc1.setup();
    this->enc2.setup();
};

SensorValues DualEncoder::get_sensors_values()
{
    // define slave bit buffer
    bool enc1_miso_buffer_bit = 0;
    bool enc2_miso_buffer_bit = 0;

    uint32_t enc_1_value = 0;
    enc_1_value <<= 16;

    uint32_t enc_2_value = 0;
    enc_2_value <<= 16;

    // set CSN low (start a frame) -------------------------------------------
    digitalWriteFast(this->pins_enc1.pin_csn, LOW);
    digitalWriteFast(this->pins_enc2.pin_csn, LOW);

    // ENCODER_BUFFER_LENGTH is 16

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value <<= 1;
    enc_2_value <<= 1;
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 2;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);

    // ---------
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_1_value <<= 1;
    enc_2_value |= enc2_miso_buffer_bit;
    enc_2_value <<= 1;
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
    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);
    enc1_miso_buffer_bit = digitalReadFast(this->pins_enc1.pin_miso);
    enc2_miso_buffer_bit = digitalReadFast(this->pins_enc2.pin_miso);
    enc_1_value |= enc1_miso_buffer_bit;
    enc_2_value |= enc2_miso_buffer_bit;

    // these last 2 bits are not important for the angle
    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);

    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);

    digitalWriteFast(this->pins_enc1.pin_sck, HIGH);
    digitalWriteFast(this->pins_enc2.pin_sck, HIGH);

    enc_1_value <<= 2;
    enc_2_value <<= 2;

    digitalWriteFast(this->pins_enc1.pin_sck, LOW);
    digitalWriteFast(this->pins_enc2.pin_sck, LOW);

    // set CSN high (end frame) -----------------------------------------------
    digitalWriteFast(this->pins_enc1.pin_csn, HIGH);
    digitalWriteFast(this->pins_enc2.pin_csn, HIGH);

    // Extract the 14 bits from the 16 bit buffer; which represent the angle step
    // ENCODER_BUFFER_enc_1_value_MASK is 14 1's

    enc_1_value = (enc_1_value & ENCODER_BUFFER_VALUE_MASK);
    enc_2_value = (enc_2_value & ENCODER_BUFFER_VALUE_MASK);

    SensorValues output = SensorValues();
    output.enc1_val = enc_1_value;
    output.enc2_val = enc_2_value;

    return output;
}