#include <Arduino.h>
#include <imxrt.h>

void log_adc_and_angle_ascii(uint32_t SIGNAL_A, uint32_t SIGNAL_B, uint32_t SIGNAL_C, uint32_t SIGNAL_VN, uint16_t ANGLE_STEP, bool ANGLE_PARITY)
{
  // Serial.print(ANGLE_PARITY);
  // Serial.print("\t");
  Serial.print(ANGLE_STEP);
  Serial.print("\t");
  Serial.print(SIGNAL_A);
  Serial.print("\t");
  Serial.print(SIGNAL_B);
  Serial.print("\t");
  Serial.print(SIGNAL_C);
  Serial.print("\t");
  Serial.print(SIGNAL_VN);
  Serial.print("\n");
}