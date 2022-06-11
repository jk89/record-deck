#include <Arduino.h>
#include <imxrt.h>

#include "./pwm.cpp"
#include "./adc.cpp"
#include "./xbar.cpp"

#define A_SD 1

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
  analogWrite(A_SD, LOW);

  disableADCTriggers();
}

void four_channel_adc_start() {
    analogWrite(A_SD, 1);
    enableADCTriggers();
}


void logLatestADCMeasurement() {
    // volatile uint32_t
    // ADC_DONE_TIMER int 32
    // ADC1_SIGNAL_A int
    // ADC1_SIGNAL_B int
    // ADC1_SIGNAL_C int
    // ADC1_SIGNAL_VN int
    cli();
    Serial.print(micros_delay);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_A);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_B);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_C);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_VN);Serial.print("\n");
    sei();
    delayMicroseconds(micros_delay); // 1000hz
    // delayMicroseconds(50); // 10khz 
    // delayMicroseconds(20); // 50khz
}

void log_adc_and_angle_ascii() {
  cli();
    Serial.print(ADC1_SIGNAL_A);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_B);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_C);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_VN);Serial.print("\n");
  sei();
}