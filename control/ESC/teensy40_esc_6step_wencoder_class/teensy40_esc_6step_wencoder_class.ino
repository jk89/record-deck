#include "./lib/motor_controller.cpp"
#include "./lib/types.h"

MotorWithThrustDirectionProfile MOTOR_CONTROLLER;

void setup()
{
  // put your setup code here, to run once:
  MotorPins motor_pins = MotorPins();
  motor_pins.pin_a_in = 2;
  motor_pins.pin_b_in = 9;
  motor_pins.pin_c_in = 8;
  motor_pins.pin_a_sd = 1;
  motor_pins.pin_b_sd = 0;
  motor_pins.pin_c_sd = 7;
  motor_pins.pin_fault_led = 13;

  EncoderPins enc_pins = EncoderPins();
  enc_pins.pin_csn = 10;
  enc_pins.pin_miso =  12;
  enc_pins.pin_mosi = 11;
  enc_pins.pin_sck = 22;

  Encoder enc = Encoder(enc_pins);

  MotorArguments motor_args = MotorArguments();
  motor_args.max_number_of_transitions_in_reverse_permitted_during_normal_operation = 1;
  motor_args.max_number_of_transitions_in_reverse_permitted_during_startup = 1;
  motor_args.pwm_frequency = 36000;
  motor_args.startup_duty = 20;
  // motor_args.state_map
  motor_args.startup_required_number_successful_transitions = 6;

  MOTOR_CONTROLLER = MotorWithThrustDirectionProfile(motor_pins, enc, motor_args);

  MOTOR_CONTROLLER.setup();
}

void loop()
{
  // put your main code here, to run repeatedly:
  MOTOR_CONTROLLER.loop();
  MOTOR_CONTROLLER.take_user_input();
}
