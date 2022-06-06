
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