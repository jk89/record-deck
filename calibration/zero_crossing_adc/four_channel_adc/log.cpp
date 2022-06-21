#include <Arduino.h>
#include <imxrt.h>

void log_adc_ascii(uint32_t time, uint32_t signal_a, uint32_t signal_b, uint32_t signal_c, uint32_t signal_vn)
{
  Serial.print(time);
  Serial.print("\t");
  Serial.print(signal_a);
  Serial.print("\t");
  Serial.print(signal_b);
  Serial.print("\t");
  Serial.print(signal_c);
  Serial.print("\t");
  Serial.print(signal_vn);
  Serial.print("\n");
}

struct AdcBitfield
{
    unsigned int time: 16;
    unsigned int signal_a: 12;
    unsigned int signal_b: 12;
    unsigned int signal_c: 12;
    unsigned int signal_vn: 12;
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

  Serial.write(message_buffer, ADC_BITFIELD_N_BYTES)
}