#include <Arduino.h>
#include <imxrt.h>

#include "./pwm.cpp"
#include "./adc.cpp"
#include "./xbar.cpp"

#define A_SD 1
#define LED_EN 13
#define PWM_FREQUENCY 1000

void main_setup()
{
  pinMode(A_SD, OUTPUT);
  pinMode(LED_EN, OUTPUT);

  adcPreConfigure();
  xbarInit();
  adcInit();
  adcEtcInit();
  pwmInit(PWM_FREQUENCY);

  // force off everything
  analogWrite(A_SD, LOW);

  disableADCTriggers();
}

void main_start() {
    analogWrite(A_SD, 1);
    enableADCTriggers();
}


void logLatestMeasurement() {
    // volatile uint32_t
    // ADC_DONE_TIMER int 32
    // ADC1_SIGNAL_A int
    // ADC1_SIGNAL_B int
    // ADC1_SIGNAL_C int
    // ADC1_SIGNAL_VN int
    cli();
    Serial.print(ADC1_SIGNAL_A);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_B);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_C);Serial.print("\t");
    Serial.print(ADC1_SIGNAL_VN);Serial.print("\n");
    sei();
    delayMicroseconds(1000); // 1000hz
    // delayMicroseconds(50); // 10khz 
    // delayMicroseconds(20); // 50khz
}
