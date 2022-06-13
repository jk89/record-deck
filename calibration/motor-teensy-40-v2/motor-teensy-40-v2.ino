// Copyright Jonathan Kelsey 2021

// goal: 3 phase brushless motor commutation based on bemf adc measurements synced to pwm cycle off state
#define DEBUG_MODE true

#include <Arduino.h>
#include "imxrt.h"
#include <ADC.h>
#include "four_channel_adc/pwm.cpp"
#include "four_channel_adc/xbar.cpp"
#include "four_channel_adc/adc.cpp"
#include "four_channel_adc/main.cpp"
#include "AS5147P/main.cpp"



#define PWM_FREQUENCY 1950

void setup()
{
  four_channel_adc_setup(PWM_FREQUENCY);
}

void loop()
{
}
