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

    this->kalman_state[0] = 0;
    this->kalman_state[1] = 0;
    this->kalman_state[2] = 0;
    this->kalman_state[3] = 0;
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

        this->get_initial_P(dt);

        // kalman_state = self.perform_kalman(dt)

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
        this->eular_state[1] = last_x + dx;
        this->eular_state[2] = v;
        this->eular_state[3] = a;
        this->eular_state[4] = j;

        // kalman_state = self.perform_kalman(dt)
    }
}