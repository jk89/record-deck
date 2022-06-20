#define PIN_TEENSY_SLAVE_RESET 3
#define PIN_TEENSY_SLAVE_CLK 4

#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"

volatile uint32_t TIME_CTR = 0;

int DEBOUNCE_DISTANCE_RESET = 100;
elapsedMicros delta_time;

void MASTER_RESET_RISING() {
  // debounce
  bool last_state = false;
  for (int i = 0; i < DEBOUNCE_DISTANCE_RESET; i++) {
    bool state = digitalReadFast(PIN_TEENSY_SLAVE_RESET);
    if (state != HIGH) {
      return;
    }
  }
  TIME_CTR = 0;
  delta_time = 0;
  /*cli();
  // this fires in error
  TIME_CTR = 0;
  Serial.print("reset ");
  Serial.print(last_state);
  Serial.print("\n");
  sei();*/
}

int DEBOUNCE_DISTANCE_CLK = 1;


void MASTER_CLK_RISING() {

  // debounce
  /*bool last_state = false;
  for (int i = 0; i < DEBOUNCE_DISTANCE_CLK; i++) {
    bool state = digitalReadFast(PIN_TEENSY_SLAVE_RESET);
    if (state != HIGH) {
      return;
    }
  }*/
  cli();
  TIME_CTR++;
  // take encoder reading
  uint16_t value = 0;
  bool angle_read_parity = as5147p_get_sensor_value(value);
  Serial.print(TIME_CTR);
  Serial.print("\t");
  Serial.print(value);
  Serial.print("\t");
  // 
  Serial.print(((float) TIME_CTR / (float) delta_time) * 1e6);
  // delta_time [micros] / (TIME_CTR) 1e6
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
