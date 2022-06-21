#define PIN_TEENSY_SLAVE_RESET 3
#define PIN_TEENSY_SLAVE_CLK 4

#include <Arduino.h>
#include "imxrt.h"
#include "AS5147P/main.cpp"
#include "encoder_slave/log.cpp"
#include "encoder_slave/main.cpp"

void setup()
{
  encoder_slave_setup();
}

void loop() {

}
