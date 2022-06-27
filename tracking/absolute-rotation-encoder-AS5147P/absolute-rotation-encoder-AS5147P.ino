#include "AS5147P/main.cpp"

void setup() {
  as5147p_setup();
}

uint16_t value;

/*
 #define PIN_CSN 10
#define PIN_SCK 22
#define PIN_MISO 12
#define PIN_MOSI 11
 */
void loop() {
  // put your main code here, to run repeatedly:
  auto parity = as5147p_get_sensor_value(value);
  Serial.print(value);
  Serial.print("\t");
  Serial.print(parity);
  Serial.print("\n");
  // delayMicroseconds(1000); // 1000hz
  delayMicroseconds(100); // 10000hz
}
