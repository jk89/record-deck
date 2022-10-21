#include <Arduino.h>
#include <imxrt.h>

#include "./com.cpp"
#include "./pwm.cpp"
#include "./adc.cpp"
#include "./xbar.cpp"

float PWM_FREQ = 0;
uint32_t micros_delay = 0;

void four_channel_adc_setup(float frequency)
{
  PWM_FREQ = frequency;
  micros_delay = (int) ((1 / PWM_FREQ) / 1e-6);

  pinMode(A_SD, OUTPUT);

  adcPreConfigure();
  xbarInit();
  adcInit();
  adcEtcInit();
  pwmInit(frequency);

  // force off everything
  four_channel_adc_stop();

  disableADCTriggers();
}