# record-deck project description

Smooth BLDC with a positional encoder, via a constant jerk model with input smoothing via a kalman filter, suitable for low to high (28k) rpm applications

## Directory layout

- /control
    - Motor control library (bldc)
    - PID library
    - Tests
- /datasets
    - scripts for downloading and processing datasets
    - /data
        folder to contain datasets
- /mechanical-design
    - details of motor design
- /calibration
    - Tools for creating an angular zero-cross calibration map
    - Tools for collecting angular zero-cross measurements
- /tracking
    - Resources needed to create a kalman filter with a jerk model
- /mechanical-design
    - File for motor mechanical design
- /scripts
    - Useful scripts to run various software contained in this repository

## [Software usage tips](https://github.com/jk89/record-deck/blob/main/USAGE.md)
## [Work logbook](https://github.com/jk89/record-deck/blob/main/resources/log.pdf)

# Authors:
- Steve Kelsey
- Jonathan Kelsey

# record-deck research

## Encoders

As a record deck is a low rpm motor we need an angular position sensor because bemf sensing will not be reliable due to high noise.

### Overview
- [Rotary encoder sensor overview1](https://www.electronicproducts.com/absolute-position-sensing-the-key-to-better-brushless-dc-motor-control/)
- [Rotary encoder sensor overview2](https://www.seeedstudio.com/blog/2020/01/19/rotary-encoders-how-it-works-how-to-use-with-arduino/)

### AS5600
- [AS5600 tutorial video](https://www.youtube.com/watch?v=yvrpIYc9Ll8&ab_channel=CuriousScientist)
- [as5600 shopping](https://coolcomponents.co.uk/products/grove-12-bit-magnetic-rotary-position-sensor-encoder-as5600?currency=GBP&variant=29543511785533&utm_medium=cpc&utm_source=google&utm_campaign=Google%20Shopping&gclid=Cj0KCQjw-JyUBhCuARIsANUqQ_I9FStKhB8IkzvJTuQMaKLdNIeIcQSBaGcPF18BLhQgqsYaSaarSBcaAqASEALw_wcB)
- [as5600 arduino overview](https://curiousscientist.tech/blog/as5600-nema17-speed-and-position)
- [AS5600 datasheet](https://ams.com/documents/20143/36005/AS5600_DS000365_5-00.pdf)

### AS5147P
- [ coding-for-as5147-rotary-sensor-by-ams arduino](https://forum.arduino.cc/t/coding-for-as5147-rotary-sensor-by-ams/342631)
- [AS5X47 arduino library](https://github.com/Adrien-Legrand/AS5X47)
- [AS5147P datasheet](https://ams.com/documents/20143/36005/AS5147P_DS000328_2-00.pdf/847d41be-7afa-94ad-98c2-8617a5df5b6f)
- [github Adrien-Legrand/AS5X47 ReadAngle.ino example](https://github.com/Adrien-Legrand/AS5X47/blob/master/examples/ReadAngle/ReadAngle.ino)
- [AS5147P-TS_EK_AB mouser shop](https://www.mouser.co.uk/ProductDetail/ams/AS5147P-TS_EK_AB?qs=Rt6VE0PE%2FOfngSpzc2DH8w%3D%3D&mgh=1&vip=1&gclid=Cj0KCQjwm6KUBhC3ARIsACIwxBjypycJOODZLcuEXv6ZZNorVRH8abVcmWROeClnLvezKtGCmwOAK5UaArH_EALw_wcB)
- [AS5147P-TS_EK_AB digikey shop](https://www.digikey.co.uk/en/products/detail/ams/AS5147P-TS_EK_AB/5452349?utm_adgroup=General&utm_source=google&utm_medium=cpc&utm_campaign=Smart%20Shopping_Product_Zombie%20SKUs&utm_term=&productid=5452349&gclid=Cj0KCQjwm6KUBhC3ARIsACIwxBh5SEG6c91mfVuQ5gbXSg_R_VdLVSx8Lk0mh_X--0qedxmupdKV2ysaAiGNEALw_wcB)
- [github MarginallyClever AS5147Test](https://github.com/MarginallyClever/AS5147Test)
- [AS5147P datasheet](https://ams.com/documents/20143/36005/AS5147P_DS000328_2-00.pdf)

AS5147P is chosen due to its 14-bit accuracy 16384 step accuracy, its high sampling rate up to 10Mhz and its high rpm performace... useful for higher speed applications. 

## Control and tracking

### Tracking

Angular velocity, acceleration and jerk will be computed using the Eular method from temporal and angular measurements, some effort is required to smooth these measurements and deal with error. Kalman or more specifically EKF will be used.

### Double pendulum kalman experiment results:

- Experiment one [alpha50 stdevx1/6 stdev_j0.00016 stdev_j0.0001 dataset_14](https://github.com/jk89/record-deck/blob/FEATURES/kalman-filter/tracking/charts/alpha50_stdevx1div6_stdev_j0.00016_stdev_j0.0001_dataset_14/VIEW_CHARTS.md)

### Useful links

- [A_jerk_model_to_tracking_highly_maneuvering_targets](https://www.researchgate.net/publication/3002819_A_jerk_model_to_tracking_highly_maneuvering_targets)
- [Jerk stackoverflow](https://dsp.stackexchange.com/questions/24847/wrong-estimation-of-derivatives-with-an-extended-kalman-filter)

- [Kalman-Filter-CA.py constant acceleration example](https://github.com/balzer82/Kalman/blob/master/Kalman-Filter-CA.py)

### Control

Control will be achieved by setting targets for angular velocity, acceleration and jerk (3rd derivative) and utalising a PID circuit to modify the motors duty cycle to compensate for dynamic and systematic drag, maintaining a precise angular velocity and achieving that speed with grace.

- [Velocity_PID](https://deltamotion.com/support/webhelp/rmctools/Controller_Features/Control_Modes/Velocity_PID.htm)

[Tuning PID control parameters with a Kalman filter](https://folk.ntnu.no/skoge/prost/proceedings/PID-2018/0064.PDF)

![image](https://github.com/jk89/record-deck/blob/main/resources/overview.png)

## Optimisation / smoothing

- [Improving the Angular Velocity Measured with a Low-Cost Magnetic Rotary Encoder Attached to a Brushed DC Motor by Compensating Magnet and Hall-Effect Sensor Misalignments](https://www.mdpi.com/1424-8220/21/14/4763)

## NXP similar project

- [Freescale NXP quad encoder bldc](https://www.nxp.com/docs/en/application-note/AN1961.pdf)

## Display

- [OLED](https://www.youtube.com/watch?v=QIR3VQ-qO94&ab_channel=ElectronicClinic)

## Useful teensy stuff

- [pjrc T4-Comparators-and-XBAR](https://forum.pjrc.com/threads/57359-T4-Comparators-and-XBAR)

## Input (pots, capitive touch, )
