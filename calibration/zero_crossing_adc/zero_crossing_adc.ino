#include <Arduino.h>
#include "imxrt.h"
#include "four_channel_adc/main.cpp"

#define PWM_FREQUENCY 300000

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
