#include <Arduino.h>
#include <imxrt.h>

void log_adc_ascii(uint32_t signal_a, uint32_t signal_b, uint32_t signal_c, uint32_t signal_vn) // uint32_t time, 
{
  // Serial.print(time);
  // Serial.print("\t");
  Serial.print(signal_a);
  Serial.print("\t");
  Serial.print(signal_b);
  Serial.print("\t");
  Serial.print(signal_c);
  Serial.print("\t");
  Serial.print(signal_vn);
  Serial.print("\n");
}

/* 
python draft

# tips https://stackoverflow.com/questions/59731963/extract-12-bit-integer-from-2-byte-big-endian-motorola-bytearray
# https://docs.python.org/3.7/library/struct.html#format-characters
# https://stackoverflow.com/questions/29529979/10-or-12-bit-field-data-type-in-c

import struct
val, _ = struct.unpack( '!cccccccc', b'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' )
time = (val >> (12*4*8)) & 0xFFFF
signal_a = (val >> (12*3*8)) & 0xFFF
signal_b = (val >> (12*2*8)) & 0xFFF
signal_c = (val >> (12*1*8)) & 0xFFF
signal_vn = val & 0xFFF

*/
struct AdcBitfield
{
    unsigned int time: 16; // 1, 2 [XXXXXXXX,XXXXXXXX]
    unsigned int signal_a: 12; // 3 , 4 [XXXXXXXX, XXXX0000]
    unsigned int signal_b: 12; // 4, 5 [0000XXXX, XXXXXXXX]
    unsigned int signal_c: 12; // 6, 7 [XXXXXXXX, XXXX0000]
    unsigned int signal_vn: 12; // 7, 8 [0000XXXX, XXXXXXXX]
};

#define ADC_BITFIELD_N_BYTES ((int)((16 + (12*4)) / 8))

void log_adc_binary(uint32_t time, uint32_t signal_a, uint32_t signal_b, uint32_t signal_c, uint32_t signal_vn) {
  AdcBitfield adc_bitfield;
  adc_bitfield.time = time;
  adc_bitfield.signal_a = signal_a;
  adc_bitfield.signal_b = signal_b;
  adc_bitfield.signal_c = signal_c;
  adc_bitfield.signal_vn = signal_vn;

  char* adc_bitfield_bytes = (char*) &adc_bitfield;
  char message_buffer[ADC_BITFIELD_N_BYTES];

  for (int i =0; i < ADC_BITFIELD_N_BYTES; i++) {
    message_buffer[i] = adc_bitfield_bytes[i];
  }

  Serial.write(message_buffer, ADC_BITFIELD_N_BYTES);
}