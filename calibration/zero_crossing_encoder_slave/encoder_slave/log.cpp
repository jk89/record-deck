#include <Arduino.h>
#include <imxrt.h>


void log_encoder_ascii(uint32_t time, uint32_t angle_step, float delta_time) {
  cli();
  Serial.print(time);
  Serial.print("\t");
  Serial.print(angle_step);
  Serial.print("\t");
  Serial.print(((float) TIME_CTR / delta_time) * 1e6); // tmp
  Serial.print("\n");
  sei();
}

/*
python draft

# tips https://stackoverflow.com/questions/59731963/extract-12-bit-integer-from-2-byte-big-endian-motorola-bytearray
# https://docs.python.org/3.7/library/struct.html#format-characters
# https://stackoverflow.com/questions/29529979/10-or-12-bit-field-data-type-in-c

import struct
val, _ = struct.unpack( '!cccccccc', b'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' )
time = (val >> (4+12)) & 0xFFFF
signal_a = val & 0xFFF

*/

struct EncoderBitfield
{
    unsigned int time: 16; // 1,2 [XXXXXXXX, XXXXXXXX]
    unsigned int padding: 4; // 3 [XXXX0000]
    unsigned int angle_step: 12; // 3, 4 [0000XXXX,XXXXXXXX]
};
#define ENCODER_BITFIELD_N_BYTES ((int)((16 + 12) / 8))

void log_encoder_binary(uint32_t time, uint32_t angle_step) {  
  EncoderBitfield encoder_bitfield;
  encoder_bitfield.time = time;
  encoder_bitfield.angle_step = angle_step;

  char* encoder_bitfield_bytes = (char*) &encoder_bitfield;
  char message_buffer[ENCODER_BITFIELD_N_BYTES];

  for (int i =0; i < ENCODER_BITFIELD_N_BYTES; i++) {
    message_buffer[i] = encoder_bitfield_bytes[i];
  }

  Serial.write(message_buffer, ENCODER_BITFIELD_N_BYTES)
}