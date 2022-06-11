#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"
#include "four_channel_adc/main.cpp"

#define PWM_FREQUENCY 10000

void setup() {
  four_channel_adc_setup(PWM_FREQUENCY);
}

bool started = false;

void loop() {
  if (started == false) {
    four_channel_adc_start();
    started = true;
  }
  logLatestADCMeasurement();
}
