

void pwmInit_1_0(float frequency)
{ // this works ok pin 1
  analogWriteFrequency(1, frequency);
  FLEXPWM1_SM0TCTRL = FLEXPWM_SMTCTRL_OUT_TRIG_EN(1 << 3);
}

// sync clocks of flexpwm1_SM0 and flexpwm1_SM1
/*
  CLK_SEL
  Clock Source Select
  These read/write bits determine the source of the clock signal for this submodule.
  00b - The IPBus clock is used as the clock for the local prescaler and counter.
  01b - EXT_CLK is used as the clock for the local prescaler and counter.
  10b - Submodule 0’s clock (AUX_CLK) is used as the source clock for the local prescaler and
  counter. This setting should not be used in submodule 0 as it will force the clock to logic 0.
  11b - reserved
*/

void pwmInit(float frequency)
{
  analogWriteRes(8);
  pwmInit_1_0(frequency);
  // pwmInit_1_1();
  // pwmInit_4_0();
}

// END PWM CTRL -----------------------------------------------------------------------------------------------------------
