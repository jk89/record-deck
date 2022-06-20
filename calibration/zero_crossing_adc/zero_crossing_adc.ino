#define PIN_TEENSY_SLAVE_RESET 3
#define PIN_TEENSY_SLAVE_CLK 4

#include <Arduino.h>
#include "imxrt.h"
#include "four_channel_adc/main.cpp"
// #include "four_channel_adc/log.cpp"

#define PWM_FREQUENCY 90000// 95000 log speed // 5000 is about the limit of plotter

void setup()
{
  pinMode(PIN_TEENSY_SLAVE_CLK, OUTPUT);
  pinMode(PIN_TEENSY_SLAVE_RESET, OUTPUT);
  digitalWriteFast(PIN_TEENSY_SLAVE_CLK, LOW);
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, LOW);

  // send reset pulse
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, HIGH);
  delayMicroseconds(100);
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, LOW);

  // startup adc
  four_channel_adc_setup(PWM_FREQUENCY);
  four_channel_adc_start();
}

void loop() {}
