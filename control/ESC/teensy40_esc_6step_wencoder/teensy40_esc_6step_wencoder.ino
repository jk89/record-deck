#include "AS5147P/main.cpp"
#include "lib/motor1.cpp"

unsigned int DIRECTION = 0;
unsigned int THRUST = 0;

#include "lib/coms.cpp"

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:
  readHostControlProfile();
  cli();
  Serial.print("DIRECTION\t");
  Serial.print(DIRECTION);
  Serial.print("\t");
    Serial.print("THRUST\t");
  Serial.print(THRUST);
  Serial.print("\n");
  sei();
}
