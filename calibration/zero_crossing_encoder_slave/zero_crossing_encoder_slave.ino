#define PIN_TEENSY_SLAVE_RESET 3
#define PIN_TEENSY_SLAVE_CLK 4

#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"

volatile uint32_t TIME_CTR = 0;

void MASTER_RESET_RISING() {
  TIME_CTR = 0;
}

void MASTER_CLK_RISING() {
  // take encoder reading
  uint16_t value = 0;
  bool angle_read_parity = as5147p_get_sensor_value(value);
  cli();
  Serial.print(TIME_CTR);
  Serial.print("\t");
  Serial.print(value);
  Serial.print("\n");  
  sei();
}

void setup()
{
  pinMode(PIN_TEENSY_SLAVE_CLK, INPUT);
  pinMode(PIN_TEENSY_SLAVE_RESET, INPUT);

  attachInterrupt(digitalPinToInterrupt(PIN_TEENSY_SLAVE_RESET), MASTER_RESET_RISING, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_TEENSY_SLAVE_CLK), MASTER_CLK_RISING, RISING);

  // setup encoder
  as5147p_setup();
}

void loop() {

}
