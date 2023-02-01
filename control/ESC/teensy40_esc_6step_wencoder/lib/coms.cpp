/* what profile do we want

from host: 2^12 maximum for thrust setting FLEXPWM would have a freq of 36621.09 Hz
so a 16 bit int would easily handle this

we also want a bit for cw or ccw

nicest way would be have 16 bit structure containing all of it therefore whole profile would be 2 bytes
*/

/*
      // struct SimpleThrustProfile *msg = (struct SimpleThrustProfile*) HOST_PROFILE_BUFFER;
      // THRUST = msg->thrust;
      // DIRECTION = msg->direction;
*/

struct SimpleThrustProfile
{
    // 1-bit unsigned field, allowed values are 0...1
    unsigned int direction; // : 1; // 0 cw 1 ccw
    // 12-bit unsigned field, allowed values are 0..4095
    unsigned int thrust; // : 12;
};

const int SIZE_OF_FLOAT = sizeof(float); // 4

// we read 2 bytes in total
const int SIZE_OF_PROFILE = 2;

char HOST_PROFILE_BUFFER[SIZE_OF_PROFILE] = {0,0};
byte HOST_PROFILE_BUFFER_CTR = 0;


bool readHostControlProfile()
{
  bool proccessedAFullProfile = false;
  cli();
  while (Serial.available()) {
    HOST_PROFILE_BUFFER[HOST_PROFILE_BUFFER_CTR] = Serial.read();
    /*Serial.print("bufferbit\t");
    Serial.print((int) HOST_PROFILE_BUFFER[HOST_PROFILE_BUFFER_CTR]);
    Serial.print("bufferctr\t");
    Serial.println(HOST_PROFILE_BUFFER_CTR);*/
    HOST_PROFILE_BUFFER_CTR++;
    if (HOST_PROFILE_BUFFER_CTR % SIZE_OF_PROFILE == 0) {
      DIRECTION = HOST_PROFILE_BUFFER[0]; // 0 is cw 1 is ccw
      THRUST = min(HOST_PROFILE_BUFFER[1], 60);

      if (THRUST == 0) {
        // this is the reset signal
        init_motor1_pwm();
      }
      else { // if (STARTUP_MODE == true)
        STARTUP_MODE = false;
      }
      proccessedAFullProfile = true;
    }
    HOST_PROFILE_BUFFER_CTR %= SIZE_OF_PROFILE;
  }
  sei();
  return proccessedAFullProfile;
}
