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
    this->q_scale = 2.0 * alpha * this->jerk_variance;
}

Kalman1D::Kalman1D(double alpha, double x_resolution_error, double x_jerk_error, double x_mod_limit)
{
    this->alpha = alpha;
    this->current_idx = -1;
    this->dbl_max = 10000000000000000000000000000000.0; // numeric_limits<double>::max();
    this->x_variance = x_resolution_error * x_resolution_error;
    this->jerk_variance = x_jerk_error * x_jerk_error;
    this->q_scale = 2.0 * alpha * this->jerk_variance;

    this->x_mod_limit = x_mod_limit;
    this->x_mod_limit_over_2 = x_mod_limit / 2.0;
    this->x_is_modular = true;

    this->eular_state[0] = 0.0;
    this->eular_state[1] = 0.0;
    this->eular_state[2] = 0.0;
    this->eular_state[3] = 0.0;
    this->eular_state[4] = 0.0;

    this->X[0] = 0.0;
    this->X[1] = 0.0;
    this->X[2] = 0.0;
    this->X[3] = 0.0;
}

double Kalman1D::calculate_diff_x(double last_x, double current_x)
{
    /* delta = (current_theta - last_theta) % self.max_theta_step
    return -(self.max_theta_step - delta) if delta > (self.max_theta_step/2) else delta*/

    if (this->x_is_modular == false)
    {
        return (current_x - last_x);
    }
    else
    {
        double delta = fmod(current_x - last_x, this->x_mod_limit);
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
    return current_t - last_t;
    /*if (current_t < last_t)
    {
        // overflow!
        return (this->dbl_max - last_t) + current_t;
    }
    else
    {
        // current time might be 20, last time might be 10
        return current_t - last_t;
    }*/
}

void Kalman1D::get_initial_P(double dt)
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

    // [row][col]
    this->p[0][0] = this->x_variance;
    this->p[0][1] = this->x_variance / dt;
    this->p[0][2] = this->x_variance / t2;
    this->p[0][3] = 0.0;

    this->p[1][0] = this->x_variance / dt;
    this->p[1][1] = (2.0 * this->x_variance) / t2;
    this->p[1][2] = (3.0 * this->x_variance) / t3;
    this->p[1][3] = (5.0 * t2 * this->jerk_variance) / 6.0;

    this->p[2][0] = this->x_variance / t2;
    this->p[2][1] = (3.0 * this->x_variance) / t3;
    this->p[2][2] = (6.0 * this->x_variance) / t4;
    this->p[2][3] = this->jerk_variance * dt;

    this->p[3][0] = 0.0;
    this->p[3][1] = (5.0 * this->jerk_variance * t2) / 6.0;
    this->p[3][2] = this->jerk_variance * dt;
    this->p[3][3] = this->jerk_variance;
}

void Kalman1D::get_Q_low_alpha_T(double dt)
{
    double t7over256 = pow(dt, 7.0) / 256.0;
    double t6over72 = pow(dt, 6.0) / 72.0;
    double t5 = pow(dt, 5.0);
    double t5over30 = t5 / 30.0;
    double t5over20 = t5 / 20.0;
    double t4 = pow(dt, 4.0);
    double t4over8 = t4 / 8.0;
    double t4over24 = t4 / 24.0;
    double t3 = pow(dt, 3.0);
    double t3over6 = t3 / 6.0;
    double t3over3 = t3 / 3.0;
    double t2over2 = pow(dt, 2.0) / 2.0;

    /*
        T7Over256 = (T**7)/256
        T6Over72 = (T ** 6)/72
        T5Over30 = (T ** 5)/30
        T5Over20 = (T ** 5)/20
        T4Over24 = (T ** 4)/24
        T4Over8 = (T ** 4)/8
        T3Over6 = (T**3)/6
        T3Over3 = (T**3)/3
        T2Over2 = (T**2)/2

        return np.matrix([
            [T7Over256, T6Over72, T5Over30, T4Over24],
            [T6Over72 , T5Over20, T4Over8 , T3Over6 ],
            [T5Over30 , T4Over8 , T3Over3 , T2Over2],
            [T4Over24 , T3Over6 , T2Over2 , T]
        ]) * self.q
    */

    // [row][col]
    this->q[0][0] = t7over256 * q_scale;
    this->q[0][1] = t6over72 * q_scale;
    this->q[0][2] = t5over30 * q_scale;
    this->q[0][3] = t4over24 * q_scale;

    this->q[1][0] = t6over72 * q_scale;
    this->q[1][1] = t5over20 * q_scale;
    this->q[1][2] = t4over8 * q_scale;
    this->q[1][3] = t3over6 * q_scale;

    this->q[2][0] = t5over30 * q_scale;
    this->q[2][1] = t4over8 * q_scale;
    this->q[2][2] = t3over3 * q_scale;
    this->q[2][3] = t2over2 * q_scale;

    this->q[3][0] = t4over24 * q_scale;
    this->q[3][1] = t3over6 * q_scale;
    this->q[3][2] = t2over2 * q_scale;
    this->q[3][3] = dt * q_scale;
};

void Kalman1D::get_F_low_alpha_T(double dt) // dont forget to omit 0 component calculations down stream
{
    double t2over2 = pow(dt, 2.0) / 2.0;
    double t3over6 = pow(dt, 3.0) / 6.0;

    // [row][col]
    this->f[0][0] = 1.0;
    this->f[0][1] = dt;
    this->f[0][2] = t2over2;
    this->f[0][3] = t3over6;

    this->f[1][0] = 0.0;
    this->f[1][1] = 1.0;
    this->f[1][2] = dt;
    this->f[1][3] = t2over2;

    this->f[2][0] = 0.0;
    this->f[2][1] = 0.0;
    this->f[2][2] = 1.0;
    this->f[2][3] = dt;

    this->f[3][0] = 0.0;
    this->f[3][1] = 0.0;
    this->f[3][2] = 0.0;
    this->f[3][3] = 1.0;

    /*
        t2Over2 = math.pow(T,2)/2
        return np.matrix([
            [1.0, T  , t2Over2, math.pow(T,3)/6],
            [0.0, 1.0, T              , t2Over2],
            [0.0, 0.0, 1.0            , T],
            [0.0, 0.0, 0.0            , 1.0]
        ])
    */
};

void Kalman1D::kalman_step(double dx, double dt)
{
    this->get_F_low_alpha_T(dt);
    this->get_Q_low_alpha_T(dt);

    // this->eular_state[0] is time
    // this->eular_state[1] is the measurement x

    // need to calculate x_kp1 4x1 4

    /*
    X_kp1 (4, 1)
        \left[\begin{matrix}f_{11} x_{1} + f_{12} x_{2} + f_{13} x_{3} + f_{14} x_{4}\\f_{21} x_{1} + f_{22} x_{2} + f_{23} x_{3} + f_{24} x_{4}\\f_{31} x_{1} + f_{32} x_{2} + f_{33} x_{3} + f_{34} x_{4}\\f_{41} x_{1} + f_{42} x_{2} + f_{43} x_{3} + f_{44} x_{4}\end{matrix}\right]
    */

    // x is eular state and time is 0 component so x's work out to the same index
    // need to shift all f indicies by 1 as they start from 1 not 0. f00 -> f33 not f11 -> f44

    this->X_kp1[0] = this->f[0][0] * this->X[1] + this->f[0][1] * this->X[2] + this->f[0][2] * this->X[3] + this->f[0][3] * this->X[4]; // f_{11} x_{1} + f_{12} x_{2} + f_{13} x_{3} + f_{14} x_{4}
    this->X_kp1[1] = this->f[1][0] * this->X[1] + this->f[1][1] * this->X[2] + this->f[1][2] * this->X[3] + this->f[1][3] * this->X[4]; // f_{21} x_{1} + f_{22} x_{2} + f_{23} x_{3} + f_{24} x_{4}
    this->X_kp1[2] = this->f[2][0] * this->X[1] + this->f[2][1] * this->X[2] + this->f[2][2] * this->X[3] + this->f[2][3] * this->X[4]; // f_{31} x_{1} + f_{32} x_{2} + f_{33} x_{3} + f_{34} x_{4}
    this->X_kp1[3] = this->f[3][0] * this->X[1] + this->f[3][1] * this->X[2] + this->f[3][2] * this->X[3] + this->f[3][3] * this->X[4]; // f_{41} x_{1} + f_{42} x_{2} + f_{43} x_{3} + f_{44} x_{4}

    // need to calculate Y 1x1 1

    /* this->eular_state[1] is measurement now s_{k}
    - s_{km1} is last measurement

    Y (1, 1)
        \left[\begin{matrix}- 1.0 X_{kp1 11} + s_{k} - s_{km1}\end{matrix}\right] // s_{k} - s_{km1} current - last x aka dx
    */

    //
    double y = -this->X_kp1[0] + dx;

    // need to calculate p_kp1 P4x4

    /*

    P_kp1 (4, 4)
    \left[\begin{matrix}f_{11} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{12} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{13} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{14} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{11} & f_{21} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{22} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{23} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{24} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{12} & f_{31} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{32} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{33} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{34} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{13} & f_{41} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{42} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{43} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{44} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{14}\\f_{11} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{12} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{13} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{14} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{21} & f_{21} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{22} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{23} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{24} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{22} & f_{31} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{32} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{33} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{34} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{23} & f_{41} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{42} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{43} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{44} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{24}\\f_{11} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{12} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{13} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{14} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{31} & f_{21} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{22} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{23} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{24} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{32} & f_{31} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{32} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{33} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{34} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{33} & f_{41} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{42} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{43} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{44} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{34}\\f_{11} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{12} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{13} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{14} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{41} & f_{21} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{22} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{23} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{24} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{42} & f_{31} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{32} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{33} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{34} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{43} & f_{41} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{42} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{43} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{44} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{44}\end{matrix}\right]


    \left[\begin{matrix}

    f_{11} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{12} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{13} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{14} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{11} & f_{21} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{22} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{23} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{24} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{12} & f_{31} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{32} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{33} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{34} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{13} & f_{41} \left(f_{11} p_{11} + f_{12} p_{21} + f_{13} p_{31} + f_{14} p_{41}\right) + f_{42} \left(f_{11} p_{12} + f_{12} p_{22} + f_{13} p_{32} + f_{14} p_{42}\right) + f_{43} \left(f_{11} p_{13} + f_{12} p_{23} + f_{13} p_{33} + f_{14} p_{43}\right) + f_{44} \left(f_{11} p_{14} + f_{12} p_{24} + f_{13} p_{34} + f_{14} p_{44}\right) + q_{14}
    f_{11} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{12} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{13} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{14} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{21} & f_{21} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{22} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{23} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{24} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{22} & f_{31} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{32} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{33} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{34} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{23} & f_{41} \left(f_{21} p_{11} + f_{22} p_{21} + f_{23} p_{31} + f_{24} p_{41}\right) + f_{42} \left(f_{21} p_{12} + f_{22} p_{22} + f_{23} p_{32} + f_{24} p_{42}\right) + f_{43} \left(f_{21} p_{13} + f_{22} p_{23} + f_{23} p_{33} + f_{24} p_{43}\right) + f_{44} \left(f_{21} p_{14} + f_{22} p_{24} + f_{23} p_{34} + f_{24} p_{44}\right) + q_{24}
    f_{11} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{12} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{13} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{14} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{31} & f_{21} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{22} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{23} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{24} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{32} & f_{31} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{32} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{33} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{34} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{33} & f_{41} \left(f_{31} p_{11} + f_{32} p_{21} + f_{33} p_{31} + f_{34} p_{41}\right) + f_{42} \left(f_{31} p_{12} + f_{32} p_{22} + f_{33} p_{32} + f_{34} p_{42}\right) + f_{43} \left(f_{31} p_{13} + f_{32} p_{23} + f_{33} p_{33} + f_{34} p_{43}\right) + f_{44} \left(f_{31} p_{14} + f_{32} p_{24} + f_{33} p_{34} + f_{34} p_{44}\right) + q_{34}
    f_{11} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{12} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{13} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{14} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{41} & f_{21} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{22} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{23} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{24} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{42} & f_{31} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{32} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{33} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{34} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{43} & f_{41} \left(f_{41} p_{11} + f_{42} p_{21} + f_{43} p_{31} + f_{44} p_{41}\right) + f_{42} \left(f_{41} p_{12} + f_{42} p_{22} + f_{43} p_{32} + f_{44} p_{42}\right) + f_{43} \left(f_{41} p_{13} + f_{42} p_{23} + f_{43} p_{33} + f_{44} p_{43}\right) + f_{44} \left(f_{41} p_{14} + f_{42} p_{24} + f_{43} p_{34} + f_{44} p_{44}\right) + q_{44}

    */

    /*
    this->f[11] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[12] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[13] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[14] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[11] & this->f[21] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[22] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[23] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[24] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[12] & this->f[31] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[32] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[33] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[34] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[13] & this->f[41] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[42] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[43] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[44] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[14]
    this->f[11] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[12] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[13] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[14] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[21] & this->f[21] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[22] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[23] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[24] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[22] & this->f[31] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[32] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[33] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[34] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[23] & this->f[41] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[42] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[43] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[44] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[24]
    this->f[11] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[12] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[13] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[14] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[31] & this->f[21] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[22] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[23] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[24] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[32] & this->f[31] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[32] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[33] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[34] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[33] & this->f[41] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[42] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[43] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[44] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[34]
    this->f[11] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[12] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[13] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[14] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[41] & this->f[21] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[22] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[23] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[24] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[42] & this->f[31] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[32] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[33] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[34] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[43] & this->f[41] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[42] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[43] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[44] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[44]
    */

    /*

    [44] => [3][3]
    [43] => [3][2]
    [34] => [2][3]
    [33] => [2][2]
    [32] => [2][1]
    [31] => [2][1]
    [24] => [1][3]
    [23] => [1][2]
    [22] => [1][1]
    [31] => []
    [21] => [1][0]
    [11] => [0][0]
    replace

    4 with &3
    3 with &2
    2 with &1
    1 with &0

    remove &

    */

    // [row][col]
    // this->f[11] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[12] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[13] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[14] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[11]
    // this->f[21] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[22] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[23] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[24] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[12]
    // this->f[31] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[32] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[33] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[34] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[13]
    // this->f[41] \left(this->f[11] this->p[11] + this->f[12] this->p[21] + this->f[13] this->p[31] + this->f[14] this->p[41]\right) + this->f[42] \left(this->f[11] this->p[12] + this->f[12] this->p[22] + this->f[13] this->p[32] + this->f[14] this->p[42]\right) + this->f[43] \left(this->f[11] this->p[13] + this->f[12] this->p[23] + this->f[13] this->p[33] + this->f[14] this->p[43]\right) + this->f[44] \left(this->f[11] this->p[14] + this->f[12] this->p[24] + this->f[13] this->p[34] + this->f[14] this->p[44]\right) + q_[14]

    this->P_kp1[0][0] = this->f[0][0] * (this->f[0][0] * this->p[0][0] + this->f[0][1] * this->p[1][0] + this->f[0][2] * this->p[2][0] + this->f[0][3] * this->p[3][0]) + this->f[0][1] * (this->f[0][0] * this->p[0][1] + this->f[0][1] * this->p[1][1] + this->f[0][2] * this->p[2][1] + this->f[0][3] * this->p[3][1]) + this->f[0][2] * (this->f[0][0] * this->p[0][2] + this->f[0][1] * this->p[1][2] + this->f[0][2] * this->p[2][2] + this->f[0][3] * this->p[3][2]) + this->f[0][3] * (this->f[0][0] * this->p[0][3] + this->f[0][1] * this->p[1][3] + this->f[0][2] * this->p[2][3] + this->f[0][3] * this->p[3][3]) + this->q[0][0];
    this->P_kp1[0][1] = this->f[1][0] * (this->f[0][0] * this->p[0][0] + this->f[0][1] * this->p[1][0] + this->f[0][2] * this->p[2][0] + this->f[0][3] * this->p[3][0]) + this->f[1][1] * (this->f[0][0] * this->p[0][1] + this->f[0][1] * this->p[1][1] + this->f[0][2] * this->p[2][1] + this->f[0][3] * this->p[3][1]) + this->f[1][2] * (this->f[0][0] * this->p[0][2] + this->f[0][1] * this->p[1][2] + this->f[0][2] * this->p[2][2] + this->f[0][3] * this->p[3][2]) + this->f[1][3] * (this->f[0][0] * this->p[0][3] + this->f[0][1] * this->p[1][3] + this->f[0][2] * this->p[2][3] + this->f[0][3] * this->p[3][3]) + this->q[0][1];
    this->P_kp1[0][2] = this->f[2][0] * (this->f[0][0] * this->p[0][0] + this->f[0][1] * this->p[1][0] + this->f[0][2] * this->p[2][0] + this->f[0][3] * this->p[3][0]) + this->f[2][1] * (this->f[0][0] * this->p[0][1] + this->f[0][1] * this->p[1][1] + this->f[0][2] * this->p[2][1] + this->f[0][3] * this->p[3][1]) + this->f[2][2] * (this->f[0][0] * this->p[0][2] + this->f[0][1] * this->p[1][2] + this->f[0][2] * this->p[2][2] + this->f[0][3] * this->p[3][2]) + this->f[2][3] * (this->f[0][0] * this->p[0][3] + this->f[0][1] * this->p[1][3] + this->f[0][2] * this->p[2][3] + this->f[0][3] * this->p[3][3]) + this->q[0][2];
    this->P_kp1[0][3] = this->f[3][0] * (this->f[0][0] * this->p[0][0] + this->f[0][1] * this->p[1][0] + this->f[0][2] * this->p[2][0] + this->f[0][3] * this->p[3][0]) + this->f[3][1] * (this->f[0][0] * this->p[0][1] + this->f[0][1] * this->p[1][1] + this->f[0][2] * this->p[2][1] + this->f[0][3] * this->p[3][1]) + this->f[3][2] * (this->f[0][0] * this->p[0][2] + this->f[0][1] * this->p[1][2] + this->f[0][2] * this->p[2][2] + this->f[0][3] * this->p[3][2]) + this->f[3][3] * (this->f[0][0] * this->p[0][3] + this->f[0][1] * this->p[1][3] + this->f[0][2] * this->p[2][3] + this->f[0][3] * this->p[3][3]) + this->q[0][3];

    // this->f[11] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[12] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[13] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[14] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[21]
    // this->f[21] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[22] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[23] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[24] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[22]
    // this->f[31] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[32] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[33] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[34] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[23]
    // this->f[41] \left(this->f[21] this->p[11] + this->f[22] this->p[21] + this->f[23] this->p[31] + this->f[24] this->p[41]\right) + this->f[42] \left(this->f[21] this->p[12] + this->f[22] this->p[22] + this->f[23] this->p[32] + this->f[24] this->p[42]\right) + this->f[43] \left(this->f[21] this->p[13] + this->f[22] this->p[23] + this->f[23] this->p[33] + this->f[24] this->p[43]\right) + this->f[44] \left(this->f[21] this->p[14] + this->f[22] this->p[24] + this->f[23] this->p[34] + this->f[24] this->p[44]\right) + q_[24]

    this->P_kp1[1][0] = this->f[0][0] * (this->f[1][0] * this->p[0][0] + this->f[1][1] * this->p[1][0] + this->f[1][2] * this->p[2][0] + this->f[1][3] * this->p[3][0]) + this->f[0][1] * (this->f[1][0] * this->p[0][1] + this->f[1][1] * this->p[1][1] + this->f[1][2] * this->p[2][1] + this->f[1][3] * this->p[3][1]) + this->f[0][2] * (this->f[1][0] * this->p[0][2] + this->f[1][1] * this->p[1][2] + this->f[1][2] * this->p[2][2] + this->f[1][3] * this->p[3][2]) + this->f[0][3] * (this->f[1][0] * this->p[0][3] + this->f[1][1] * this->p[1][3] + this->f[1][2] * this->p[2][3] + this->f[1][3] * this->p[3][3]) + this->q[1][0];
    this->P_kp1[1][1] = this->f[1][0] * (this->f[1][0] * this->p[0][0] + this->f[1][1] * this->p[1][0] + this->f[1][2] * this->p[2][0] + this->f[1][3] * this->p[3][0]) + this->f[1][1] * (this->f[1][0] * this->p[0][1] + this->f[1][1] * this->p[1][1] + this->f[1][2] * this->p[2][1] + this->f[1][3] * this->p[3][1]) + this->f[1][2] * (this->f[1][0] * this->p[0][2] + this->f[1][1] * this->p[1][2] + this->f[1][2] * this->p[2][2] + this->f[1][3] * this->p[3][2]) + this->f[1][3] * (this->f[1][0] * this->p[0][3] + this->f[1][1] * this->p[1][3] + this->f[1][2] * this->p[2][3] + this->f[1][3] * this->p[3][3]) + this->q[1][1];
    this->P_kp1[1][2] = this->f[2][0] * (this->f[1][0] * this->p[0][0] + this->f[1][1] * this->p[1][0] + this->f[1][2] * this->p[2][0] + this->f[1][3] * this->p[3][0]) + this->f[2][1] * (this->f[1][0] * this->p[0][1] + this->f[1][1] * this->p[1][1] + this->f[1][2] * this->p[2][1] + this->f[1][3] * this->p[3][1]) + this->f[2][2] * (this->f[1][0] * this->p[0][2] + this->f[1][1] * this->p[1][2] + this->f[1][2] * this->p[2][2] + this->f[1][3] * this->p[3][2]) + this->f[2][3] * (this->f[1][0] * this->p[0][3] + this->f[1][1] * this->p[1][3] + this->f[1][2] * this->p[2][3] + this->f[1][3] * this->p[3][3]) + this->q[1][2];
    this->P_kp1[1][3] = this->f[3][0] * (this->f[1][0] * this->p[0][0] + this->f[1][1] * this->p[1][0] + this->f[1][2] * this->p[2][0] + this->f[1][3] * this->p[3][0]) + this->f[3][1] * (this->f[1][0] * this->p[0][1] + this->f[1][1] * this->p[1][1] + this->f[1][2] * this->p[2][1] + this->f[1][3] * this->p[3][1]) + this->f[3][2] * (this->f[1][0] * this->p[0][2] + this->f[1][1] * this->p[1][2] + this->f[1][2] * this->p[2][2] + this->f[1][3] * this->p[3][2]) + this->f[3][3] * (this->f[1][0] * this->p[0][3] + this->f[1][1] * this->p[1][3] + this->f[1][2] * this->p[2][3] + this->f[1][3] * this->p[3][3]) + this->q[1][3];

    // this->f[11] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[12] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[13] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[14] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[31]
    // this->f[21] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[22] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[23] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[24] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[32]
    // this->f[31] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[32] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[33] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[34] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[33]
    // this->f[41] \left(this->f[31] this->p[11] + this->f[32] this->p[21] + this->f[33] this->p[31] + this->f[34] this->p[41]\right) + this->f[42] \left(this->f[31] this->p[12] + this->f[32] this->p[22] + this->f[33] this->p[32] + this->f[34] this->p[42]\right) + this->f[43] \left(this->f[31] this->p[13] + this->f[32] this->p[23] + this->f[33] this->p[33] + this->f[34] this->p[43]\right) + this->f[44] \left(this->f[31] this->p[14] + this->f[32] this->p[24] + this->f[33] this->p[34] + this->f[34] this->p[44]\right) + q_[34]

    this->P_kp1[2][0] = this->f[0][0] * (this->f[2][0] * this->p[0][0] + this->f[2][1] * this->p[1][0] + this->f[2][2] * this->p[2][0] + this->f[2][3] * this->p[3][0]) + this->f[0][1] * (this->f[2][0] * this->p[0][1] + this->f[2][1] * this->p[1][1] + this->f[2][2] * this->p[2][1] + this->f[2][3] * this->p[3][1]) + this->f[0][2] * (this->f[2][0] * this->p[0][2] + this->f[2][1] * this->p[1][2] + this->f[2][2] * this->p[2][2] + this->f[2][3] * this->p[3][2]) + this->f[0][3] * (this->f[2][0] * this->p[0][3] + this->f[2][1] * this->p[1][3] + this->f[2][2] * this->p[2][3] + this->f[2][3] * this->p[3][3]) + this->q[2][0];
    this->P_kp1[2][1] = this->f[1][0] * (this->f[2][0] * this->p[0][0] + this->f[2][1] * this->p[1][0] + this->f[2][2] * this->p[2][0] + this->f[2][3] * this->p[3][0]) + this->f[1][1] * (this->f[2][0] * this->p[0][1] + this->f[2][1] * this->p[1][1] + this->f[2][2] * this->p[2][1] + this->f[2][3] * this->p[3][1]) + this->f[1][2] * (this->f[2][0] * this->p[0][2] + this->f[2][1] * this->p[1][2] + this->f[2][2] * this->p[2][2] + this->f[2][3] * this->p[3][2]) + this->f[1][3] * (this->f[2][0] * this->p[0][3] + this->f[2][1] * this->p[1][3] + this->f[2][2] * this->p[2][3] + this->f[2][3] * this->p[3][3]) + this->q[2][1];
    this->P_kp1[2][2] = this->f[2][0] * (this->f[2][0] * this->p[0][0] + this->f[2][1] * this->p[1][0] + this->f[2][2] * this->p[2][0] + this->f[2][3] * this->p[3][0]) + this->f[2][1] * (this->f[2][0] * this->p[0][1] + this->f[2][1] * this->p[1][1] + this->f[2][2] * this->p[2][1] + this->f[2][3] * this->p[3][1]) + this->f[2][2] * (this->f[2][0] * this->p[0][2] + this->f[2][1] * this->p[1][2] + this->f[2][2] * this->p[2][2] + this->f[2][3] * this->p[3][2]) + this->f[2][3] * (this->f[2][0] * this->p[0][3] + this->f[2][1] * this->p[1][3] + this->f[2][2] * this->p[2][3] + this->f[2][3] * this->p[3][3]) + this->q[2][2];
    this->P_kp1[2][3] = this->f[3][0] * (this->f[2][0] * this->p[0][0] + this->f[2][1] * this->p[1][0] + this->f[2][2] * this->p[2][0] + this->f[2][3] * this->p[3][0]) + this->f[3][1] * (this->f[2][0] * this->p[0][1] + this->f[2][1] * this->p[1][1] + this->f[2][2] * this->p[2][1] + this->f[2][3] * this->p[3][1]) + this->f[3][2] * (this->f[2][0] * this->p[0][2] + this->f[2][1] * this->p[1][2] + this->f[2][2] * this->p[2][2] + this->f[2][3] * this->p[3][2]) + this->f[3][3] * (this->f[2][0] * this->p[0][3] + this->f[2][1] * this->p[1][3] + this->f[2][2] * this->p[2][3] + this->f[2][3] * this->p[3][3]) + this->q[2][3];

    // this->f[11] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[12] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[13] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[14] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[41]
    // this->f[21] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[22] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[23] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[24] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[42]
    // this->f[31] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[32] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[33] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[34] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[43]
    // this->f[41] \left(this->f[41] this->p[11] + this->f[42] this->p[21] + this->f[43] this->p[31] + this->f[44] this->p[41]\right) + this->f[42] \left(this->f[41] this->p[12] + this->f[42] this->p[22] + this->f[43] this->p[32] + this->f[44] this->p[42]\right) + this->f[43] \left(this->f[41] this->p[13] + this->f[42] this->p[23] + this->f[43] this->p[33] + this->f[44] this->p[43]\right) + this->f[44] \left(this->f[41] this->p[14] + this->f[42] this->p[24] + this->f[43] this->p[34] + this->f[44] this->p[44]\right) + q_[44]

    this->P_kp1[3][0] = this->f[0][0] * (this->f[3][0] * this->p[0][0] + this->f[3][1] * this->p[1][0] + this->f[3][2] * this->p[2][0] + this->f[3][3] * this->p[3][0]) + this->f[0][1] * (this->f[3][0] * this->p[0][1] + this->f[3][1] * this->p[1][1] + this->f[3][2] * this->p[2][1] + this->f[3][3] * this->p[3][1]) + this->f[0][2] * (this->f[3][0] * this->p[0][2] + this->f[3][1] * this->p[1][2] + this->f[3][2] * this->p[2][2] + this->f[3][3] * this->p[3][2]) + this->f[0][3] * (this->f[3][0] * this->p[0][3] + this->f[3][1] * this->p[1][3] + this->f[3][2] * this->p[2][3] + this->f[3][3] * this->p[3][3]) + this->q[3][0];
    this->P_kp1[3][1] = this->f[1][0] * (this->f[3][0] * this->p[0][0] + this->f[3][1] * this->p[1][0] + this->f[3][2] * this->p[2][0] + this->f[3][3] * this->p[3][0]) + this->f[1][1] * (this->f[3][0] * this->p[0][1] + this->f[3][1] * this->p[1][1] + this->f[3][2] * this->p[2][1] + this->f[3][3] * this->p[3][1]) + this->f[1][2] * (this->f[3][0] * this->p[0][2] + this->f[3][1] * this->p[1][2] + this->f[3][2] * this->p[2][2] + this->f[3][3] * this->p[3][2]) + this->f[1][3] * (this->f[3][0] * this->p[0][3] + this->f[3][1] * this->p[1][3] + this->f[3][2] * this->p[2][3] + this->f[3][3] * this->p[3][3]) + this->q[3][1];
    this->P_kp1[3][2] = this->f[2][0] * (this->f[3][0] * this->p[0][0] + this->f[3][1] * this->p[1][0] + this->f[3][2] * this->p[2][0] + this->f[3][3] * this->p[3][0]) + this->f[2][1] * (this->f[3][0] * this->p[0][1] + this->f[3][1] * this->p[1][1] + this->f[3][2] * this->p[2][1] + this->f[3][3] * this->p[3][1]) + this->f[2][2] * (this->f[3][0] * this->p[0][2] + this->f[3][1] * this->p[1][2] + this->f[3][2] * this->p[2][2] + this->f[3][3] * this->p[3][2]) + this->f[2][3] * (this->f[3][0] * this->p[0][3] + this->f[3][1] * this->p[1][3] + this->f[3][2] * this->p[2][3] + this->f[3][3] * this->p[3][3]) + this->q[3][2];
    this->P_kp1[3][3] = this->f[3][0] * (this->f[3][0] * this->p[0][0] + this->f[3][1] * this->p[1][0] + this->f[3][2] * this->p[2][0] + this->f[3][3] * this->p[3][0]) + this->f[3][1] * (this->f[3][0] * this->p[0][1] + this->f[3][1] * this->p[1][1] + this->f[3][2] * this->p[2][1] + this->f[3][3] * this->p[3][1]) + this->f[3][2] * (this->f[3][0] * this->p[0][2] + this->f[3][1] * this->p[1][2] + this->f[3][2] * this->p[2][2] + this->f[3][3] * this->p[3][2]) + this->f[3][3] * (this->f[3][0] * this->p[0][3] + this->f[3][1] * this->p[1][3] + this->f[3][2] * this->p[2][3] + this->f[3][3] * this->p[3][3]) + this->q[3][3];

    // need to calculate K 4x1

    /*

    K (4, 1)
    \left[\begin{matrix}\frac{1.0 P_{kp1 11}}{1.0 P_{kp1 11} + vt}\\\frac{1.0 P_{kp1 21}}{1.0 P_{kp1 11} + vt}\\\frac{1.0 P_{kp1 31}}{1.0 P_{kp1 11} + vt}\\\frac{1.0 P_{kp1 41}}{1.0 P_{kp1 11} + vt}\end{matrix}\right]

    \frac{1.0 P_{kp1 11}}{1.0 P_{kp1 11} + vt}
    \frac{1.0 P_{kp1 21}}{1.0 P_{kp1 11} + vt}
    \frac{1.0 P_{kp1 31}}{1.0 P_{kp1 11} + vt}
    \frac{1.0 P_{kp1 41}}{1.0 P_{kp1 11} + vt}

    */

    this->K[0] = this->P_kp1[0][0] / (this->P_kp1[0][0] + this->jerk_variance);
    this->K[1] = this->P_kp1[1][0] / (this->P_kp1[0][0] + this->jerk_variance);
    this->K[2] = this->P_kp1[2][0] / (this->P_kp1[0][0] + this->jerk_variance);
    this->K[3] = this->P_kp1[3][0] / (this->P_kp1[0][0] + this->jerk_variance);

    // need to calculate p_kp2 4x4

    /*

    P_kp2 (4, 4)
\left[\begin{matrix}P_{kp1 11} \cdot \left(1 - 1.0 K_{11}\right) & P_{kp1 12} \cdot \left(1 - 1.0 K_{11}\right) & P_{kp1 13} \cdot \left(1 - 1.0 K_{11}\right) & P_{kp1 14} \cdot \left(1 - 1.0 K_{11}\right)\\- 1.0 K_{21} P_{kp1 11} + P_{kp1 21} & - 1.0 K_{21} P_{kp1 12} + P_{kp1 22} & - 1.0 K_{21} P_{kp1 13} + P_{kp1 23} & - 1.0 K_{21} P_{kp1 14} + P_{kp1 24}\\- 1.0 K_{31} P_{kp1 11} + P_{kp1 31} & - 1.0 K_{31} P_{kp1 12} + P_{kp1 32} & - 1.0 K_{31} P_{kp1 13} + P_{kp1 33} & - 1.0 K_{31} P_{kp1 14} + P_{kp1 34}\\- 1.0 K_{41} P_{kp1 11} + P_{kp1 41} & - 1.0 K_{41} P_{kp1 12} + P_{kp1 42} & - 1.0 K_{41} P_{kp1 13} + P_{kp1 43} & - 1.0 K_{41} P_{kp1 14} + P_{kp1 44}\end{matrix}\right]

\left[\begin{matrix}P_{kp1 11} \cdot \left(1 - 1.0 K_{11}\right) & P_{kp1 12} \cdot \left(1 - 1.0 K_{11}\right) & P_{kp1 13} \cdot \left(1 - 1.0 K_{11}\right) & P_{kp1 14} \cdot \left(1 - 1.0 K_{11}\right)
- 1.0 K_{21} P_{kp1 11} + P_{kp1 21} & - 1.0 K_{21} P_{kp1 12} + P_{kp1 22} & - 1.0 K_{21} P_{kp1 13} + P_{kp1 23} & - 1.0 K_{21} P_{kp1 14} + P_{kp1 24}
- 1.0 K_{31} P_{kp1 11} + P_{kp1 31} & - 1.0 K_{31} P_{kp1 12} + P_{kp1 32} & - 1.0 K_{31} P_{kp1 13} + P_{kp1 33} & - 1.0 K_{31} P_{kp1 14} + P_{kp1 34}
- 1.0 K_{41} P_{kp1 11} + P_{kp1 41} & - 1.0 K_{41} P_{kp1 12} + P_{kp1 42} & - 1.0 K_{41} P_{kp1 13} + P_{kp1 43} & - 1.0 K_{41} P_{kp1 14} + P_{kp1 44}



    */

    this->P_kp2[0][0] = this->P_kp1[0][0] * (1.0 - this->K[0]);
    this->P_kp2[0][1] = this->P_kp1[0][1] * (1.0 - this->K[0]);
    this->P_kp2[0][2] = this->P_kp1[0][2] * (1.0 - this->K[0]);
    this->P_kp2[0][3] = this->P_kp1[0][3] * (1.0 - this->K[0]);

    this->P_kp2[1][0] = -this->K[1] * this->P_kp1[0][0] + this->P_kp1[1][0];
    this->P_kp2[1][1] = -this->K[1] * this->P_kp1[0][1] + this->P_kp1[1][1];
    this->P_kp2[1][2] = -this->K[1] * this->P_kp1[0][2] + this->P_kp1[1][2];
    this->P_kp2[1][3] = -this->K[1] * this->P_kp1[0][3] + this->P_kp1[1][3];

    this->P_kp2[2][0] = -this->K[2] * this->P_kp1[0][0] + this->P_kp1[2][0];
    this->P_kp2[2][1] = -this->K[2] * this->P_kp1[0][1] + this->P_kp1[2][1];
    this->P_kp2[2][2] = -this->K[2] * this->P_kp1[0][2] + this->P_kp1[2][2];
    this->P_kp2[2][3] = -this->K[2] * this->P_kp1[0][3] + this->P_kp1[2][3];

    this->P_kp2[3][0] = -this->K[3] * this->P_kp1[0][0] + this->P_kp1[3][0];
    this->P_kp2[3][1] = -this->K[3] * this->P_kp1[0][1] + this->P_kp1[3][1];
    this->P_kp2[3][2] = -this->K[3] * this->P_kp1[0][2] + this->P_kp1[3][2];
    this->P_kp2[3][3] = -this->K[3] * this->P_kp1[0][3] + this->P_kp1[3][3];

    // need to calculate x_kp2 (kalman) 4x1 4

    /*

    X_kp1_final (4, 1)
\left[\begin{matrix}K_{11} Y_{11} + X_{kp1 11}\\K_{21} Y_{11} + X_{kp1 21}\\K_{31} Y_{11} + X_{kp1 31}\\K_{41} Y_{11} + X_{kp1 41}\end{matrix}\right]


K_{11} Y_{11} + X_{kp1 11}
K_{21} Y_{11} + X_{kp1 21}
K_{31} Y_{11} + X_{kp1 31}
K_{41} Y_{11} + X_{kp1 41}

    */

   this->X[0] = this->K[0] * y + this->X_kp1[0];
   this->X[1] = this->K[1] * y + this->X_kp1[1];
   this->X[2] = this->K[2] * y + this->X_kp1[2];
   this->X[3] = this->K[3] * y + this->X_kp1[3];


   

    // error 11

    /*

    kalman_error (1, 1)
\left[\begin{matrix}1.0 p_{11}\end{matrix}\right]

    */
}

void Kalman1D::step(double time, double x)
{
    if (this->current_idx == -1) // update state with time and x
    {
        this->eular_state[0] = time;
        this->eular_state[1] = x;
        this->eular_state[2] = 0.0;
        this->eular_state[3] = 0.0;
        this->eular_state[4] = 0.0;

        this->current_idx++;
    }
    else if (this->current_idx == 0) // update state with time x and calculated eular estimate for v
    {
        double last_time = this->eular_state[0];
        double last_x = this->eular_state[1];

        double dt = this->calculate_diff_t(last_time, time);
        double dx = this->calculate_diff_x(last_x, x);
        double v = dx / dt;

        this->eular_state[0] = time;
        this->eular_state[1] = last_x + dx;
        this->eular_state[2] = v;
        this->eular_state[3] = 0.0;
        this->eular_state[4] = 0.0;

        this->current_idx++;
    }
    else if (this->current_idx == 1) // update state with time x and calculated eular estimate for v and a. Enough to estimate kalman assuming starting with 0 jerk. Make this an option
    {
        double last_time = this->eular_state[0];
        double last_x = this->eular_state[1];
        double last_v = this->eular_state[2];

        double dt = this->calculate_diff_t(last_time, time);
        double dx = this->calculate_diff_x(last_x, x);
        double v = dx / dt;
        double a = (v - last_v) / dt;

        this->eular_state[0] = time;
        this->eular_state[1] = last_x + dx;
        this->eular_state[2] = v;
        this->eular_state[3] = a;
        this->eular_state[4] = 0.0;

        this->X[0] = eular_state[1];
        this->X[1] = eular_state[2];
        this->X[2] = eular_state[3];
        this->X[3] = eular_state[4];

        this->get_initial_P(dt);

        this->kalman_step(dx, dt);

        this->current_idx++;
    }
    else // update state with time x and calculated eular estimate for v, a and j. Perform kalman as we have a full state estimate.
    {

        double last_time = this->eular_state[0];
        double last_x = this->eular_state[1];
        double last_v = this->eular_state[2];
        double last_a = this->eular_state[3];

        double dt = this->calculate_diff_t(last_time, time);
        double dx = this->calculate_diff_x(last_x, x);
        double v = dx / dt;
        double a = (v - last_v) / dt;
        double j = (a - last_a) / dt;

        this->eular_state[0] = time;
        this->eular_state[1] = last_x + dx; // wont this introduce drift?
        // calculate a deviation away from encoder reading in future?
        this->eular_state[2] = v;
        this->eular_state[3] = a;
        this->eular_state[4] = j;

        this->kalman_step(dx, dt);
    }
}