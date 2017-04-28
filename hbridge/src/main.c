#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include "gpa_scpi.h"
#include "avg_adc.h"
#include <util/delay.h>

#define SCPI_USART USARTF0

void setClockTo32MHz() {
    CCP = CCP_IOREG_gc;              // disable register security for oscillator update
    OSC.CTRL = OSC_RC32MEN_bm;       // enable 32MHz oscillator
    while(!(OSC.STATUS & OSC_RC32MRDY_bm)); // wait for oscillator to be ready
    CCP = CCP_IOREG_gc;              // disable register security for clock update
    CLK.CTRL = CLK_SCLKSEL_RC32M_gc; // switch to 32MHz clock
}

void usart_sendc(char c){
    while( !(SCPI_USART.STATUS & USART_DREIF_bm) ); //Wait until DATA buffer is empty
    SCPI_USART.DATA = c;
}

void usart_send(const char* s){
    while(*s){
        usart_sendc(*s);
        s++;
    }
}

void usart_int(uint16_t i, uint8_t base){
    char  buf[16];
    itoa(i, buf, base);
    usart_send(buf);
}

void scpi_print(const char *s){
    usart_send(s);
}

void usart_init(){
    SCPI_USART.BAUDCTRLB = 0xD0;
    SCPI_USART.BAUDCTRLA = 131;
    SCPI_USART.CTRLC = USART_CHSIZE_8BIT_gc;
    SCPI_USART.CTRLA = USART_RXCINTLVL_LO_gc;
    SCPI_USART.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
    PORTF.DIRSET = (1 << 3);
}

void setup(){
    PMIC.CTRL = PMIC_LOLVLEN_bm|PMIC_MEDLVLEN_bm|PMIC_HILVLEN_bm;
    sei();
    usart_init();
    //usart_send("Hello world!\r\n");
    adc_init();
}
volatile uint8_t do_process = 0;
volatile static char buf[64];


void update(){
    //usart_send("B\n\r");
    if(do_process){
        scpi_execute((char*)buf);
        do_process = 0;

    }
    //_delay_ms(100);
}



int main(void){
    setClockTo32MHz();
    setup();
    while(1){
        update();
    }
    return -1;
}



ISR(USARTF0_RXC_vect){
    static uint8_t indx = 0;
    static uint8_t mindx = 0;
    char tmp = SCPI_USART.DATA;
    buf[indx] = tmp;
/*    if(tmp == '\b' && indx > 0){
        indx --;
        usart_send("\b \b");
        return;
    }*/
    //usart_sendc(tmp);//Echo
    if(tmp == '\n'){
        buf[indx] = '\0';
        do_process = 1;
        indx = mindx = 0;
    }else{
        indx++;
        mindx++;
    }
}