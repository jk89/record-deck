#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"
#include "TeensyTimerTool.h"
using namespace TeensyTimerTool;

volatile uint32_t latest_angle;
volatile uint32_t angle_tick = 0;
volatile uint32_t elapsed_seconds = 0;
PeriodicTimer t1(GPT1);

void setup() {
  as5147p_setup();
  t1.begin(callback, 1_Hz);
}


void loop() {
  latest_angle = as5147p_get_sensor_value_fast();
  angle_tick += 1;
}

void callback() {
  elapsed_seconds++;
  float refresh_rate = (float) angle_tick / ((float) elapsed_seconds);
  Serial.print(refresh_rate);
  Serial.print("\t");
  Serial.print(latest_angle);
  Serial.print("\n");
}
