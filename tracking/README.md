# Tracking Hardware

For this project I will be using a AS5147P magnetic rotary encoder to determine absolute position of the rotor shaft. [Read more.](./absolute-rotation-encoder-AS5147P/README.md)

# Tracking Software

Angular velocity, acceleration and jerk will be computed using the Eular method from temporal and angular measurements, some effort is required to smooth these measurements and deal with error. Kalman or more specifically EKF will be used.

## Tracking software

### State estimation graphing software for validation:
REQUIRES: Installing the [IBM double pendulum dataset](../datasets/README.md).
In the root project directory run...
- npm run simulate:double-pendulum --dataset=14

### Perform BLDC duty simulation
In the root project directory run...
- npm run simulate:bldc

## Results

### Double pendulum kalman experiment results:

- Experiment one [alpha50 stdevx1/6 stdev_j1 dataset_14](charts/alpha50_stdevx1div6_stdev_j1_dataset_14/VIEW_CHARTS.md)
  
- Experiment two [alpha50 stdevx1/6 stdev_x0.00016 stdev_j0.0001 dataset_14](charts/alpha50_stdevx1div6_stdev_j0.00016_stdev_j0.0001_dataset_14/VIEW_CHARTS.md)

- Experiment three [alpha50 stdevx1/6 stdev_x0.00016 stdev_j0.00001 dataset_14](charts/alpha50_stdevx1div6_stdev_j0.00001_dataset_14/VIEW_CHARTS.md)

### BLDC duty simulation results:

- [Logistic function](charts/simulations/VIEW_CHARTS.md)

## Useful links

- [A_jerk_model_to_tracking_highly_maneuvering_targets](https://www.researchgate.net/publication/3002819_A_jerk_model_to_tracking_highly_maneuvering_targets)
- [Jerk stackoverflow](https://dsp.stackexchange.com/questions/24847/wrong-estimation-of-derivatives-with-an-extended-kalman-filter)

- [Kalman-Filter-CA.py constant acceleration example](https://github.com/balzer82/Kalman/blob/master/Kalman-Filter-CA.py)
