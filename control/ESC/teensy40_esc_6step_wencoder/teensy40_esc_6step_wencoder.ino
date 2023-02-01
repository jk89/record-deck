unsigned int DIRECTION = 0;
unsigned int THRUST = 0;

#include "AS5147P/main.cpp"
#include "lib/motor1.cpp"
#include "lib/coms.cpp"

void setup()
{
  // put your setup code here, to run once:
  init_motor1_pwm();
}

void loop()
{
  // put your main code here, to run repeatedly:
  if (STARTUP_MODE == false) // main loop
  {
    uint32_t angle = as5147p_get_sensor_value_fast();
    
    // get relevant state map
    int MOTOR_1_NEW_STATE = STATE_MAP[DIRECTION][angle]; // 16384

    if (MOTOR_1_NEW_STATE != MOTOR_1_STATE)
    {
      // we have a new state
      // enforce commutation
      enforce_motor1_state(MOTOR_1_NEW_STATE);
      // update motor state cache
      MOTOR_1_STATE = MOTOR_1_NEW_STATE;
    }
      // Serial.print("started\t");
    // Serial.println(DIRECTION);
  }
  readHostControlProfile();
  cli();
  Serial.print("trueVal\t");
  Serial.print(true);
  Serial.print("\t");
  Serial.print("DIRECTION\t");
  Serial.print(DIRECTION);
  Serial.print("\t");
  Serial.print("THRUST\t");
  Serial.print(THRUST);
  Serial.print("\t");
  Serial.print("IN_STARTUP_MODE\t");
  Serial.print(STARTUP_MODE);
  Serial.print("\t");
  Serial.print("\n");
  sei();
}
