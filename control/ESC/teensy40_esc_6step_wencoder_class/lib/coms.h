template <class T, uint8_t size_of_profile>
class SerialInputController {
    private:
    T current_profile;
    byte host_profile_buffer_ctr;
    char host_profile_buffer[size_of_profile];
    public:
    SerialInputController();
    bool readProfile();
    T getProfile();
    void setup();
};

const int SIZE_OF_THRUST_DIRECTION_PROFILE = 2;
using SerialInputControllerThrustDirectionProfile = SerialInputController<ThrustDirectionProfile, SIZE_OF_THRUST_DIRECTION_PROFILE>;
