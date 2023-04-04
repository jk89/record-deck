#include "kalman.hpp"
#include <math.h>
// #include <limits>

Kalman1D::Kalman1D(double alpha, double x_resolution_error, double x_jerk_error)
{
    this->alpha = alpha;
    this->x_is_modular = false;
    this->current_idx = -1;
    this->dbl_max = 10000000000000000000000000000000000.0; // numeric_limits<double>::max();
    this->x_variance = x_resolution_error * x_resolution_error;
    this->jerk_variance = x_jerk_error * x_jerk_error;
}

Kalman1D::Kalman1D(double alpha, double x_resolution_error, double x_jerk_error, double x_mod_limit)
{
    this->alpha = alpha;
    this->current_idx = -1;
    this->dbl_max = 10000000000000000000000000000000.0; // numeric_limits<double>::max();
    this->x_variance = x_resolution_error * x_resolution_error;
    this->jerk_variance = x_jerk_error * x_jerk_error;

    this->x_mod_limit = x_mod_limit;
    this->x_mod_limit_over_2 = x_mod_limit / 2.0;
    this->x_is_modular = true;

    this->eular_state[0][0] = 0;
    this->eular_state[1][0] = 0;
    this->eular_state[2][0] = 0;
    this->eular_state[3][0] = 0;

    this->kalman_state[0][0] = 0;
    this->kalman_state[1][0] = 0;
    this->kalman_state[2][0] = 0;
    this->kalman_state[3][0] = 0;
}

void Kalman1D::kalman_step()
{
}

double Kalman1D::calculate_diff_x(double last_x, double current_x)
{
    /* delta = (current_theta - last_theta) % self.max_theta_step
     return -(self.max_theta_step - delta) if delta > (self.max_theta_step/2) else delta*/
    double delta;

    if (this->x_is_modular == false)
    {
        delta = (current_x - last_x);
        return delta;
    }
    else
    {
        delta = fmod(current_x - last_x, this->x_mod_limit);
        if (delta > this->x_mod_limit_over_2)
        {
            return -(this->x_mod_limit - delta);
        }
        else
        {
            return delta;
        }
    }
}

double Kalman1D::calculate_diff_t(double last_t, double current_t)
{
    if (current_t < last_t)
    {
        // overflow!
        return (this->dbl_max - last_t) + current_t
    }
    else
    {
        // current time might be 20, last time might be 10
        return current_t - last_t;
    }
}

ndArr Kalman1D::get_initial_P(double dt)
{

    /*
        T2 = T ** 2
        T3 = T ** 3
        T4 = T ** 4
        return np.matrix([
            [self.variance_theta   , self.variance_theta/T         , self.variance_theta/T2    , 0                   ],
            [self.variance_theta/T , (2*self.variance_theta)/T2    , (3*self.variance_theta)/T3, ((5*self.variance_jerk)/6)*T2],
            [self.variance_theta/T2, (3*self.variance_theta)/T3    , (6*self.variance_theta)/T4, self.variance_jerk * T       ],
            [0           , ((5*self.variance_jerk*T2)/6), self.variance_jerk*T     , self.variance_jerk]
        ])
    */

    double t2 = pow(dt, 2.0);
    double t3 = pow(dt, 3.0);
    double t4 = pow(dt, 4.0);
    P _p;
    // [row][col]
    _p[0][0] = this->x_variance;
    _p[0][1] = this->x_variance / dt;
    _p[0][2] = this->x_variance / t2;
    _p[0][3] = 0.0;

    _p[1][0] = this->x_variance / dt;
    _p[1][1] = (2.0 * this->x_variance) / t2;
    _p[1][2] = (3.0 * this->x_variance) / t3;
    _p[1][3] = (5.0 * t2 * this->jerk_variance) / 6.0;

    _p[2][0] = this->x_variance / t2;
    _p[2][1] = (3.0 * this->x_variance) / t3;
    _p[2][2] = (6.0 * this->x_variance) / t4;
    _p[2][3] = this->jerk_variance * dt;

    _p[3][0] = 0.0;
    _p[3][1] = (5.0 * this->jerk_variance * t2) / 6.0;
    _p[3][2] = this->jerk_variance * dt;
    _p[3][3] = this->jerk_variance;

    return *_p;
}

ndArr Kalman1D::get_Q_low_alpha_T(double dt){};
ndArr Kalman1D::get_F_low_alpha_T(double dt){};

void Kalman1D::step(double time, double x)
{
    this->current_idx = -1;

    if (this->current_idx == -1)
    {

        // X[4][1] X new_state = {{time}, {x}, {0}, {0}};
        this->eular_state[0][0] = time;
        this->eular_state[1][0] = x;
        this->eular_state[2][0] = 0;
        this->eular_state[3][0] = 0;
    }
    else if (this->current_idx == 0)
    {
        double last_time = this->eular_state[0][0];
        double last_x = this->eular_state[1][0];
    }
}

/*
    if current_idx == -1:
        # just add time and theta
        self.states.append((measurement[0], measurement[1], 0, 0, 0))

        current_time = measurement[0]
        current_theta = measurement[1]

                dt = self.calculate_diff_time(last_time, current_time)
        ds = self.calculate_diff_theta(last_theta, current_theta)

*/