#include <Arduino.h>
#include "imxrt.h"
#include "adc/main.cpp"

void setup() {
  // put your setup code here, to run once:
  main_setup();
}

bool started = false;

void loop() {
  if (started == false) {
    main_start();
    started = true;
  }
  logLatestMeasurement();
}
