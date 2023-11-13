#include "./coms.h"
#include "./types.h"

// generic functions

template <class T, uint8_t size_of_profile>
SerialInputController<T, size_of_profile>::SerialInputController()
{
    this->host_profile_buffer_ctr = 0;
    this->host_profile_buffer = {};
    this->current_profile = T();
}

template <class T, uint8_t size_of_profile>
T SerialInputController<T, size_of_profile>::getProfile()
{
    return this->current_profile;
}

template <class T, uint8_t size_of_profile>
void SerialInputController<T, size_of_profile>::setup()
{
    // delay serial read as too early and it gets junk noise data
    while (!Serial.available())
    {
        delay(100);
    }
}

// Thrust direction profile implementation

int THRUST_DIRECTION_PROFILE_THRUST_LIMIT = 20;

template <>
bool SerialInputControllerThrustDirectionProfile::readProfile()
{
    cli(); // no interrupt
    bool proccessedAFullProfile = false;
    while (Serial.available())
    {
        this->host_profile_buffer[this->host_profile_buffer_ctr] = Serial.read(); // read byte from usb
        this->host_profile_buffer_ctr++;                                          // in buffer
        if (this->host_profile_buffer_ctr % SIZE_OF_THRUST_DIRECTION_PROFILE == 0)
        {                                                                                             // when we have the right number of bytes for the whole input profile
            this->current_profile.direction = this->host_profile_buffer[0];                           // extract direction from buffer (0 is cw 1 is ccw)
            this->current_profile.thrust = min(this->host_profile_buffer[1], THRUST_DIRECTION_PROFILE_THRUST_LIMIT); // Limit thrust to 20 artifically for safety for now FIXME remove
            proccessedAFullProfile = true;                                                                           // indicate we have processed a full profile
        }
        this->host_profile_buffer_ctr %= SIZE_OF_THRUST_DIRECTION_PROFILE; // reset buffer ctr for a new profile
    }
    sei(); // interrupt
    return proccessedAFullProfile;
}