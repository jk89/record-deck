#define PIN_TEENSY_SLAVE_RESET 3
#define PIN_TEENSY_SLAVE_CLK 4

#include <Arduino.h>
#include "imxrt.h"
#include "four_channel_adc/main.cpp"
// #include "four_channel_adc/log.cpp"

#define PWM_FREQUENCY 20000// 95000 log speed // 5000 is about the limit of plotter

void setup()
{
  pinMode(PIN_TEENSY_SLAVE_CLK, OUTPUT);
  pinMode(PIN_TEENSY_SLAVE_RESET, OUTPUT);
  digitalWriteFast(PIN_TEENSY_SLAVE_CLK, LOW);
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, LOW);
  asm("dsb");
  delayMicroseconds(100);

  // startup adc
  four_channel_adc_setup(PWM_FREQUENCY);

  four_channel_adc_start();

  // send reset pulse
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, HIGH);
  enableADCTriggers();
  asm("dsb");

  delayMicroseconds(50);
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, LOW);
  asm("dsb");
}

void loop() {

}
