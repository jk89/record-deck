#include <Arduino.h>
#include <imxrt.h>
#include <ADC.h>
#include "log.cpp"

// ADC MASK CONSTANTS----------------------------------------------------------------------------------------------

// trigger enable/disable masks:

// example
// 00000000|0|1|0|00000|00000000|000|0|000|0|00000111
// ADC_ETC_CTRL = 0x40000007;  // TSC_BYPASS: TSC will control ADC2 directly // trigger 0, 1 and 2 enabled

// enable trigger 0 when phase A is pwming
// |= 00000000|0|0|0|00000|00000000|000|0|000|0|00000001
volatile uint32_t ADC1_ENABLE_TRIG_ON_PHASEA_PWM_MASK = 0x01;
// disable trigger 0
// &= 11111111|1|1|1|11111|11111111|111|1|111|1|11111110
// 0xfffffffffe
volatile uint32_t ADC1_DISABLE_TRIG_ON_PHASEA_PWM_MASK = 0xfffffffffe;

// END ADC MASK CONSTANTS----------------------------------------------------------------------------------------------

// ADC GLOBALS --------------------------------------------------------------------------------------------------------


// adc tmp value holders
volatile uint32_t TMP_ADC1_SIGNAL_A, TMP_ADC1_SIGNAL_B, TMP_ADC1_SIGNAL_C, TMP_ADC1_SIGNAL_VN = 0;

// adc value holders
int ADC1_SIGNAL_A, ADC1_SIGNAL_B, ADC1_SIGNAL_C, ADC1_SIGNAL_VN = 0;

// adc chain interrupt handlers
int ADC1_ITER_CTR = 0;

// define a time ticking clock
volatile uint32_t TIME_CTR = 0;

#define ADC_RESOLUTION 12

// ADC  -----------------------------------------------------------------------------------------------------------

void adcetc0_isr()
{
    digitalWriteFast(PIN_TEENSY_SLAVE_CLK, HIGH); // tell slave teensy to take an angular reading
    asm("dsb");
    ADC_ETC_DONE0_1_IRQ |= 1; // clear
    if (ADC1_ITER_CTR == 0)
    {
        TMP_ADC1_SIGNAL_A = ADC_ETC_TRIG0_RESULT_1_0 & 4095;
    }
    else
    {
        TMP_ADC1_SIGNAL_VN = ADC_ETC_TRIG0_RESULT_3_2 & 4095;
    }
    ADC1_ITER_CTR++;
    asm("dsb");
}
void adcetc1_isr()
{
    digitalWriteFast(PIN_TEENSY_SLAVE_CLK, LOW); // reset clk for next interrupt
    asm("dsb");
    ADC_ETC_DONE0_1_IRQ |= 1 << 16; // clear
    if (ADC1_ITER_CTR == 1)
    {
        TMP_ADC1_SIGNAL_B = (ADC_ETC_TRIG0_RESULT_1_0 >> 16) & 4095;
    }
    else
    {
        TMP_ADC1_SIGNAL_C = (ADC_ETC_TRIG0_RESULT_3_2 >> 16) & 4095;
    }
    ADC1_ITER_CTR++;
    TIME_CTR++;
    // we have the results of our 4 adc channels A,B,C,VN
    if (ADC1_ITER_CTR > 3)
    {
        ADC1_SIGNAL_A = TMP_ADC1_SIGNAL_A;
        ADC1_SIGNAL_B = TMP_ADC1_SIGNAL_B;
        ADC1_SIGNAL_C = TMP_ADC1_SIGNAL_C;
        ADC1_SIGNAL_VN = TMP_ADC1_SIGNAL_VN;

        cli();
        log_adc_and_angle_ascii(TIME_CTR, ADC1_SIGNAL_A, ADC1_SIGNAL_B, ADC1_SIGNAL_C, ADC1_SIGNAL_VN);
        sei();
        ADC1_ITER_CTR = 0;
    }
    asm("dsb");
}

ADC *adc = new ADC();
void adcPreConfigure()
{
    adc->adc0->setAveraging(1);
    adc->adc0->setResolution(ADC_RESOLUTION);
    adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED);
    adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED);
}

void adcInit()
{
    // init and calibrate
    analogReadResolution(ADC_RESOLUTION);
    analogRead(0);
    analogRead(1);
    // hardware trigger
    ADC1_CFG |= ADC_CFG_ADTRG;
    // External channel selection from ADC_ETC we need four channels per motor
    // motor 1 ADC 1 channel 0 -> 3
    ADC1_HC0 = 16;
    ADC1_HC1 = 16;
    ADC1_HC2 = 16;
    ADC1_HC3 = 16;
}

void adcEtcInit()
{
    ADC_ETC_CTRL &= ~(1 << 31); // SOFTRST

    // TSC_BYPASS 1
    ADC_ETC_CTRL = 0x40000000; // TSC_BYPASS 1: TSC will control ADC2 directly // trigger 0, 1 and 2 disabled

    // ADC CHANNELS WE NEED
    // 14/A0 AD_B1_02  ADC1_IN7  Analog channel 1 input 7
    // 15/A1 AD_B1_03  ADC1_IN8  Analog channel 1 input 8
    // 16/A2 AD_B1_07  ADC1_IN12 Analog channel 1 input 12
    // 17/A3 AD_B1_06  ADC1_IN11 Analog channel 1 input 11

    // setup adc trigger chain.

    ADC_ETC_TRIG0_CHAIN_1_0 = 0x50283017; // ADC1 7 8 adc channels, HWTS, IE, B2B;
    // TRIG(0/1/2)_CHAIN 1: Finished Interrupt on Done1, Enable B2B, the next ADC trigger will be sent as soon as possible. ADC hardware trigger selection:2, ADC channel selection 8
    // TRIG(0/1/2)_CHAIN 0: Finished Interrupt on Done0, Enable B2B, the next ADC trigger will be sent as soon as possible. ADC hardware trigger selection:1, ADC channel selection 7

    ADC_ETC_TRIG0_CHAIN_3_2 = 0x504c303b; // ADC1 11 12, chain channel, HWTS, IE, B2B;
    // TRIG(0/1/2)_CHAIN 3: Finished Interrupt on Done1, Enable B2B, the next ADC trigger will be sent as soon as possible. ADC hardware trigger selection:4, ADC channel selection 12
    // TRIG(0/1/2) CHAIN 2: Finished Interrupt on Done0, Enable B2B, the next ADC trigger will be sent as soon as possible. ADC hardware trigger selection:3, ADC channel selection 11

    // enable the triggers
    /*
      000000000000000000000|001|000|0|000|0 // 1) chain of 2 x100
      000000000000000000000|010|000|0|000|0 // 2) chain of 3 x200
      000000000000000000000|011|000|0|000|0 // 3) chain of 4 x300
    */
    ADC_ETC_TRIG0_CTRL = 0x300; // TRIG 0 chain length to the ADC Chain = 4

    // enable adc interrupt callbacks
    attachInterruptVector(IRQ_ADC_ETC0, adcetc0_isr);
    NVIC_ENABLE_IRQ(IRQ_ADC_ETC0);
    attachInterruptVector(IRQ_ADC_ETC1, adcetc1_isr);
    NVIC_ENABLE_IRQ(IRQ_ADC_ETC1);
}

void enableADCTriggers() {
  // enable adc trigger on phaseA pwm
  ADC_ETC_CTRL |= ADC1_ENABLE_TRIG_ON_PHASEA_PWM_MASK;
}

void disableADCTriggers() {
  // disable adc trigger on phaseA pwm
  ADC_ETC_CTRL &= ADC1_DISABLE_TRIG_ON_PHASEA_PWM_MASK;
}

// END ADC  -----------------------------------------------------------------------------------------------------------
