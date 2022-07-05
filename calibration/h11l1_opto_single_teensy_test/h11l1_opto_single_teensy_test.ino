#define OPTO_CLK_IN 7
#define OPTO_CLK_OUT 8

#include "TeensyTimerTool.h"
using namespace TeensyTimerTool;

PeriodicTimer t2(GPT1);

volatile uint32_t time_ctr1 = 0;
volatile uint32_t time_ctr2 = 0;
volatile uint32_t time_sync_lost = 0;

void OTP_CLK_IN_FALLING() {
  time_ctr2 += 1;
  // compare
  if (time_ctr1 != time_ctr2) {
    if (time_sync_lost == 0) {
      time_sync_lost = time_ctr1;
    }
  }

      cli();
    Serial.print("Sync\t");
    Serial.print(time_ctr1);
    Serial.print("\t");
    Serial.print(time_ctr2);
    Serial.print("\t");
    Serial.print(time_ctr1 - time_ctr2);
    Serial.print("\n");
    sei();
}

void FIRE_PULSE() {
  digitalWriteFast(OPTO_CLK_OUT, LOW); // inverts to high
  time_ctr1 += 1;
  delayNanoseconds(3000);
  digitalWriteFast(OPTO_CLK_OUT, HIGH); // inverts to low
}

void setup() {
  pinMode(OPTO_CLK_IN, INPUT);
  pinMode(OPTO_CLK_OUT, OUTPUT);
  
  attachInterrupt(digitalPinToInterrupt(OPTO_CLK_IN), OTP_CLK_IN_FALLING, FALLING);

  delayMicroseconds(1000);
  
  t2.begin(FIRE_PULSE, 120000_Hz); // 60000

}

void loop() {
  // put your main code here, to run repeatedly:

}
