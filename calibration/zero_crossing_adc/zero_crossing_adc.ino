#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"
#include "four_channel_adc/main.cpp"
// #include "four_channel_adc/log.cpp"

#define PWM_FREQUENCY 90000// 95000 log speed // 5000 is about the limit of plotter

void setup()
{
  // as5147p_setup();
  four_channel_adc_setup(PWM_FREQUENCY);
  four_channel_adc_start();
}

void loop() {}
