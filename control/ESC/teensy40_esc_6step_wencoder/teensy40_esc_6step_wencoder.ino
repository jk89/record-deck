unsigned int DIRECTION = 0;
unsigned int THRUST = 0;
#define DEBUG_MODE true
#include "AS5147P/main.cpp"
#include "lib/coms.cpp"
#include "lib/motor1.cpp"


void setup()
{
  // setup encoder
  as5147p_setup();
  // setup motor one
  init_motor1();
  // delay serial read as too early and it gets junk noise data
  while (!Serial.available()) {
   delay(10);
  }
}

void loop()
{
  loop_motor1();
}
