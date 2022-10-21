#include <Arduino.h>
#include <imxrt.h>
#define A_SD 1

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

void four_channel_adc_stop() {
    analogWrite(A_SD, LOW);
    // analogWrite(A_SD, 0);
}

void four_channel_adc_start() {
    analogWrite(A_SD, 1);
    // analogWrite(A_SD, 0);
}
