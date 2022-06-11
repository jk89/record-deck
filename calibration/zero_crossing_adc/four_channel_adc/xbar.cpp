#include <Arduino.h>
#include <imxrt.h>

void xbarConnect(unsigned int input, unsigned int output)
{
  if (input >= 88)
    return;
  if (output >= 132)
    return;
  volatile uint16_t *xbar = &XBARA1_SEL0 + (output / 2);
  uint16_t val = *xbar;
  if (!(output & 1))
  {
    val = (val & 0xFF00) | input;
  }
  else
  {
    val = (val & 0x00FF) | (input << 8);
  }
  *xbar = val;
}

void xbarInit()
{
  CCM_CCGR2 |= CCM_CCGR2_XBAR1(CCM_CCGR_ON); //turn clock on for xbara1
  // connect xbar pwm trigger output for the pwm signal and pipe to adc etc trigger input
  xbarConnect(XBARA1_IN_FLEXPWM1_PWM1_OUT_TRIG0, XBARA1_OUT_ADC_ETC_TRIG00); // pwm module 1.0 pin 1
}
