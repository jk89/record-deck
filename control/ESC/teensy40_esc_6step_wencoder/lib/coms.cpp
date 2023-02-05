/* what profile do we want
8 bytes direction
8 bytes thrust
*/

// we read 2 bytes in total
const int SIZE_OF_PROFILE = 2;

// buffer to store the thrust/direction profile from the serial stream
char HOST_PROFILE_BUFFER[SIZE_OF_PROFILE] = {0,0};
byte HOST_PROFILE_BUFFER_CTR = 0;

bool readHostControlProfile()
{
  bool proccessedAFullProfile = false;
  cli(); // no interrupt
  while (Serial.available()) {
    HOST_PROFILE_BUFFER[HOST_PROFILE_BUFFER_CTR] = Serial.read(); // read byte from usb
    HOST_PROFILE_BUFFER_CTR++; // in buffer
    if (HOST_PROFILE_BUFFER_CTR % SIZE_OF_PROFILE == 0) { // when we have the right number of bytes for the whole input profile
      DIRECTION = HOST_PROFILE_BUFFER[0]; // extract direction from buffer (0 is cw 1 is ccw)
      REVERSED_DIRECTION = DIRECTION == 0 ? 1 : 0; // stored reverse of direction as well 
      THRUST = min(HOST_PROFILE_BUFFER[1], 60); // Limit thrust to 60 artifically for safety for now FIXME remove
      proccessedAFullProfile = true; // indicate we have processed a full profile
    }
    HOST_PROFILE_BUFFER_CTR %= SIZE_OF_PROFILE; // reset buffer ctr for a new profile
  }
  sei(); // interrupt
  return proccessedAFullProfile;
}

// from host: 2^12 maximum for thrust setting FLEXPWM would have a freq of 36621.09 Hz so in future we need 16 bits atleast
