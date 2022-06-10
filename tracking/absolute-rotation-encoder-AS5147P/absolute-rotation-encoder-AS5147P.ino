#include "AS5147P/main.cpp"

void setup() {
  as5147p_setup();
}

uint16_t value;

void loop() {
  // put your main code here, to run repeatedly:
  auto parity = as5147p_get_raw_sensor_value(value);
  Serial.print(value);
  Serial.print("\t");
  Serial.print(parity);
  Serial.print("\n");
  delayMicroseconds(1000); // 1000hz
}
