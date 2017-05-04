//
// Created by atmelfan on 2017-04-10.
//

#include <avr/io.h>

#ifndef AVR_MAIN_AVG_ADC_H
#define AVR_MAIN_AVG_ADC_H

#endif //AVR_MAIN_AVG_ADC_H
#define ADC_VREF ADC_REFSEL_INT1V_gc
#define ADC_VREF_VOLTAGE 1.0


#define ADC_TO_VOLTAGE(x) ((x)*(ADC_VREF_VOLTAGE/4096.0))

void adc_init();

uint16_t adc_read(uint8_t ch);

