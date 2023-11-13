#include <iostream>
#include "../kalman.cpp"


int main() {
    double alpha = 1.0;
    double x_res_error = 4.0;
    double x_jerk_error = 1.0;
    Kalman1D kalman_normal = Kalman1D(alpha,x_res_error, x_jerk_error);
    double x_mod = 16384.0;
    Kalman1D kalman_modular = Kalman1D(alpha,x_res_error, x_jerk_error, x_mod);
    std::cout << "done";
}