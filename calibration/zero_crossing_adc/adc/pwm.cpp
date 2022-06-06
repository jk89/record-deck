#include <Arduino.h>
#include <imxrt.h>

void pwmInit_1_0(float frequency)
{ // this works ok pin 1
  analogWriteFrequency(1, frequency);
  FLEXPWM1_SM0TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 3);
}

void pwmInit(float frequency)
{
  analogWriteRes(8);
  pwmInit_1_0(frequency);
}
