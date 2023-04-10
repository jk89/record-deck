#include <iostream>
#include "../kalman.cpp"

void print_state(double *eular, double *kalman, double (*p)[4])
{
    std::cout << "\n";
    std::cout << "Eular\n";
    std::cout << eular[0] << ",";
    std::cout << eular[1] << ",";
    std::cout << eular[2] << ",";
    std::cout << eular[3] << ",";
    std::cout << eular[4] << "\n";

    std::cout << "Kalman\n";
    std::cout << kalman[0] << ",";
    std::cout << kalman[1] << ",";
    std::cout << kalman[2] << ",";
    std::cout << kalman[3] << "\n";

    std::cout << "p\n";
    std::cout << p[0][0] << ",";
    std::cout << p[0][1] << ",";
    std::cout << p[0][2] << ",";
    std::cout << p[0][3] << "\n";

    std::cout << p[1][0] << ",";
    std::cout << p[1][1] << ",";
    std::cout << p[1][2] << ",";
    std::cout << p[1][3] << "\n";

    std::cout << p[2][0] << ",";
    std::cout << p[2][1] << ",";
    std::cout << p[2][2] << ",";
    std::cout << p[2][3] << "\n";

    std::cout << p[3][0] << ",";
    std::cout << p[3][1] << ",";
    std::cout << p[3][2] << ",";
    std::cout << p[3][3] << "\n";
}

int main()
{
    double alpha = 100.0;
    double x_res_error = 4.0;
    double x_jerk_error = 1.0;
    Kalman1D kalman_normal = Kalman1D(alpha, x_res_error, x_jerk_error);

    std::cout << "kalman step 1";
    kalman_normal.step(1.0, 1.0);
    auto eular = kalman_normal.get_eular_state();
    auto kalman = kalman_normal.get_X();
    auto p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "kalman step 2";
    kalman_normal.step(2.0, 2.0);
    eular = kalman_normal.get_eular_state();
    kalman = kalman_normal.get_X();
    p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "kalman step 3";
    kalman_normal.step(3.0, 3.0);
    eular = kalman_normal.get_eular_state();
    kalman = kalman_normal.get_X();
    p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "kalman step 4";
    kalman_normal.step(4.0, 4.0);
    eular = kalman_normal.get_eular_state();
    kalman = kalman_normal.get_X();
    p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "kalman step 5";
    kalman_normal.step(5.0, 5.0);
    eular = kalman_normal.get_eular_state();
    kalman = kalman_normal.get_X();
    p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "kalman step 6";
    kalman_normal.step(6.0, 6.0);
    eular = kalman_normal.get_eular_state();
    kalman = kalman_normal.get_X();
    p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "kalman step 7";
    kalman_normal.step(7.0, 7.0);
    eular = kalman_normal.get_eular_state();
    kalman = kalman_normal.get_X();
    p = kalman_normal.get_P();
    print_state(eular, kalman, p);
    std::cout << "--------------------------------------------------\n";

    std::cout << "done";
}