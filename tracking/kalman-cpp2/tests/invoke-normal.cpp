#include <iostream>
#include "../kalman.cpp"

void print_state(double *eular, double *kalman, double (*p)[4]) {
    
}

int main() {
    double alpha = 1.0;
    double x_res_error = 4.0;
    double x_jerk_error = 1.0;
    Kalman1D kalman_normal = Kalman1D(alpha,x_res_error, x_jerk_error);
    kalman_normal.step(1.0, 1.0);
    auto eular = kalman_normal.get_eular_state();
    auto kalman = kalman_normal.get_X();
    auto p = kalman_normal.get_P();
    kalman_normal.step(1.0, 2.0);
    kalman_normal.step(1.0, 3.0);
    kalman_normal.step(1.0, 4.0);
    kalman_normal.step(1.0, 5.0);
    kalman_normal.step(1.0, 6.0);
    kalman_normal.step(1.0, 7.0);
    std::cout << "done";
}