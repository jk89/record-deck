void four_channel_adc_setup(float frequency) {
  adcPreConfigure();
  xbarInit();
  adcInit();
  adcEtcInit();
  pwmInit(frequency);
  ADC_ETC_CTRL |= ADC1_ENABLE_TRIG_ON_PHASEA_PWM_MASK;
}