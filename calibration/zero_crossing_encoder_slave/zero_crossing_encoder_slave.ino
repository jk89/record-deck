#define PIN_TEENSY_SLAVE_RESET 3 // opto (brown lead)
#define PIN_TEENSY_SLAVE_CLK 7 // opto in blue (green lead)

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
