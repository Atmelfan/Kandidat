#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>

#define SCPI_USART USARTE0

void setClockTo32MHz() {
    CCP = CCP_IOREG_gc;              // disable register security for oscillator update
    OSC.CTRL = OSC_RC32MEN_bm;       // enable 32MHz oscillator
    while(!(OSC.STATUS & OSC_RC32MRDY_bm)); // wait for oscillator to be ready
    CCP = CCP_IOREG_gc;              // disable register security for clock update
    CLK.CTRL = CLK_SCLKSEL_RC32M_gc; // switch to 32MHz clock
}

void usart_send(char* s){
    while(*s){
        while( !(SCPI_USART.STATUS & USART_DREIF_bm) ); //Wait until DATA buffer is empty
        SCPI_USART.DATA = *s;
        s++;
    }
}

void usart_int(uint16_t i, uint8_t base){
    char  buf[16];
    itoa(i, buf, base);
    usart_send(buf);
}

void usart_init(){
    SCPI_USART.BAUDCTRLB = 0xD0;
    SCPI_USART.BAUDCTRLA = 131;
    SCPI_USART.CTRLC = USART_CHSIZE_8BIT_gc;
    SCPI_USART.CTRLA = USART_RXCINTLVL_LO_gc;
    SCPI_USART.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
}

void setup(){
    PMIC.CTRL = PMIC_LOLVLEN_bm|PMIC_MEDLVLEN_bm|PMIC_HILVLEN_bm;
    sei();


}

void update(){

}

int main(void){
    setClockTo32MHz();
    setup();
    while(1){
        update();
    }
    return -1;
}

ISR(USARTC1_)