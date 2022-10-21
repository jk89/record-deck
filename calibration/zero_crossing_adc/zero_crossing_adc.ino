#define PIN_TEENSY_SLAVE_RESET 3 // (brown lead)
#define PIN_TEENSY_SLAVE_CLK 8 // opto in blue (green lead)
#define PWM_FREQUENCY 90000 //100000// 40000 most tested// 60000 unstable// 30000// 12000 // 8000 unstable // 7000// 6000 stable ish// 5000 is stable// 95000 log speed // 5000 is about the limit of plotter

bool started = false;

#include <Arduino.h>
#include "imxrt.h"
#include "four_channel_adc/main.cpp"

void setup()
{
  pinMode(PIN_TEENSY_SLAVE_CLK, OUTPUT);
  pinMode(PIN_TEENSY_SLAVE_RESET, OUTPUT);
  digitalWriteFast(PIN_TEENSY_SLAVE_CLK, HIGH);
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, HIGH);
  asm("dsb");
  delayMicroseconds(100);
  // startup adc
  four_channel_adc_setup(PWM_FREQUENCY);
}

void loop() {
  if (started == false) {
    wait_for_first_byte();    

    // send reset pulse
    digitalWriteFast(PIN_TEENSY_SLAVE_RESET, LOW);
    enableADCTriggers();
    four_channel_adc_start();
    asm("dsb");

    delayMicroseconds(50);
    digitalWriteFast(PIN_TEENSY_SLAVE_RESET, HIGH);
    asm("dsb");

  }
  started = true;
}
