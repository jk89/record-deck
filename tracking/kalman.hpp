/*
 *
 * Developed for the Dronium Project
 * This product includes software developed by Jonathan Kelsey
 * (gitlink).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/**
 * @brief Jerk model
 *  Implemention following this paper:
 *  [Ref1]: https://www.researchgate.net/publication/3002819_A_jerk_model_to_tracking_highly_maneuvering_targets/link/00b7d51f03ca864666000000/download
 * 
 *  Definitions
 *  -------------------------------------------
 *  t: time
 *  k: a step index of the system
 *  j(t): jerk as a function of time
 *  w(t): white noise applying only to jerk as a function of time
 *  w_{k}: white noise at step k
 *  tau: a small time
 *  r_j(tau): jerk correlation as a function of a small time
 *  sigma_j: standard deviation of target jerk
 *  alpha: varience of w(t)
 *  delta(tau): the unit impulse function or "deltafunction"
 *  r_w(tau): auto correlation of the white noise input
 *  absolute value of variable g: ||g||
 *  q: the transform of the white noise w(t) that drives j(t)
 *  X_{k}: state of the system at step k. e.g. [position,velocity, acceleration, jerk]
 *  X_{k+1}: state of the system at step t+1. e.g. [position,velocity, acceleration, jerk]
 *  dt: the real world time measured difference between consecutive steps k and k+1
 *  u(k): process noise as a function of steps
 *  B: jerk extractor matrix
 *  F(k+1,k): state transition matrix as defined in [Ref1] low alpha tau (T in the reference) regiume, from step k to k+1
 *  Q(dt): The variance matrix of the process noise u(k) as a function of dt
 *  P(dt): covariance matrix initalisation as a function of dt
 *  
 *  jerk defined as:
 *  j(t) = - alpha * j(t) + w(t)
 * 
 *  jerk correlation defined as:
 *  r_j(tau) = sigma_j^2 * exp(-alpha*||tau||)
 * 
 *  white noise correlation defined as:
 *  r_w(tau) = 2 * alpha * sigma_j^2 * delta(tau) = q * delta(tau)
 *  
 *  q defined as:
 *  q = 2 * alpha * sigma_j^2
 *  
 *  B defined as:
 *  B = transpose([0, 0, 0, 1])
 * 
 *  F
 * 
 *  Method:
 *  -----------------------------------------------
 *  take last known state X_{k} and project it ahead in time, one step forward:
 *  X_{k+1} = F(k+1, k) * X_{k} + B * w_{k}
 *  note B adds w_{k} to jerk component of (F(k+1, k) * X_{k})
 *  
 *  Project the error covariance ahead:
 *  P = F*self.last_p*F.T + Q    
 * 
 */


   /* # create H (is the measurement matrix)
    self.H = np.matrix([[1.0, 0.0, 0.0, 0.0]])
    # create R
    self.R = np.matrix([[self.variance_theta]])
*/

/* Measurement matrix */
typedef float H[1][4];

/* Measurement Noise Covariance vector */
typedef float R[1][1];

// # Error covariance matrix

class Kalman1D {
private:
    /// @brief 
    float alpha;
    float x_resolution_error;
    float x_jerk_error;
    bool x_is_modular;
protected:
public:
    /**
     * Kalman1D constructor.
     *
     * @param x_resolution_error The standard deviation of a measurement variable x
     * @param x_jerk_error The standard deviation constraint of the 4th temporal derivative of a measurement variable x
     * @param alpha alpha used to calculate q factor with q = 2 * alpha * x_jerk_error^2 
     * @return instance of Kalman1D class
     */
    Kalman1D(float alpha, float x_resolution_error, float x_jerk_error) {

    }

    /**
     * Kalman1D constructor.
     *
     * @param x_resolution_error The standard deviation of a measurement variable x
     * @param x_jerk_error The standard deviation constraint of the 4th temporal derivative of a measurement variable x
     * @param alpha alpha used to calculate q factor with q = 2 * alpha * x_jerk_error^2 
     * @param x_mod_limit If x obeys modular arithmatic what is the maximum value before restarting x at 0 
     * @return instance of Kalman1D class
     */
    Kalman1D(float alpha, float x_resolution_error, float x_jerk_error, double x_mod_limit) {

    }
};