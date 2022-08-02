#define PIN_TEENSY_SLAVE_RESET 3 // (brown lead)
#define PIN_TEENSY_SLAVE_CLK 8 // opto in blue (green lead)

#include <Arduino.h>
#include "imxrt.h"
#include "four_channel_adc/main.cpp"
// #include "four_channel_adc/log.cpp"

#define PWM_FREQUENCY 20000// 95000 log speed // 5000 is about the limit of plotter

void setup()
{
  pinMode(PIN_TEENSY_SLAVE_CLK, OUTPUT);
  pinMode(PIN_TEENSY_SLAVE_RESET, OUTPUT);
  digitalWriteFast(PIN_TEENSY_SLAVE_CLK, HIGH);
  digitalWriteFast(PIN_TEENSY_SLAVE_RESET, HIGH);
  asm("dsb");
  delayMicroseconds(100);




  // startup adc
  four_channel_adc_setup(PWM_FREQUENCY);


}

int byte_count = 0;
bool wait_for_first_byte() {
  while (!Serial.available()) {
     delay(100);
     Serial.println("waiting");
  }
  Serial.read();
  return true;
}

bool started = false;
void loop() {
  if (started == false) {

    wait_for_first_byte();
    Serial.println("go");
    four_channel_adc_start();

    // send reset pulse
    digitalWriteFast(PIN_TEENSY_SLAVE_RESET, LOW);
    enableADCTriggers();
    asm("dsb");

    delayMicroseconds(50);
    digitalWriteFast(PIN_TEENSY_SLAVE_RESET, HIGH);
    asm("dsb");

  }
  started = true;

}
