#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"
#include "four_channel_adc/main.cpp"
// #include "four_channel_adc/log.cpp"

#define PWM_FREQUENCY 95000

void setup()
{
  as5147p_setup();
  four_channel_adc_setup(PWM_FREQUENCY);
  four_channel_adc_start();
}

void loop() {}
