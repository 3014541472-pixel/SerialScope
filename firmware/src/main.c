/* STM32F103C8: HSI 8 MHz, USART1 115200 8N1, ADC1 channel 0 (PA0).
 * Register definitions follow ST RM0008. No HAL or external oscillator needed.
 */
#include <stdint.h>
#define REG(a) (*(volatile uint32_t *)(a))
#define RCC_CR REG(0x40021000)
#define RCC_CFGR REG(0x40021004)
#define RCC_APB2ENR REG(0x40021018)
#define GPIOA_CRL REG(0x40010800)
#define GPIOA_CRH REG(0x40010804)
#define USART_SR REG(0x40013800)
#define USART_DR REG(0x40013804)
#define USART_BRR REG(0x40013808)
#define USART_CR1 REG(0x4001380c)
#define ADC_SR REG(0x40012400)
#define ADC_CR2 REG(0x40012408)
#define ADC_SMPR2 REG(0x40012410)
#define ADC_SQR1 REG(0x4001242c)
#define ADC_SQR3 REG(0x40012434)
#define ADC_DR REG(0x4001244c)
#define SYST_CSR REG(0xe000e010)
#define SYST_RVR REG(0xe000e014)
#define SYST_CVR REG(0xe000e018)
#ifndef DEMO_MODE
#define DEMO_MODE 1
#endif
#ifndef VREF_MV
#define VREF_MV 3300u
#endif
static void delay_ms(uint32_t ms) {
    SYST_RVR = 7999; SYST_CVR = 0; SYST_CSR = 5;
    while (ms--) { while (!(SYST_CSR & (1u << 16))) {} }
    SYST_CSR = 0;
}
static void uart_text(const char *p) {
    while (*p) { while (!(USART_SR & (1u << 7))) {} USART_DR = (uint8_t)*p++; }
}
static void uart_uint(uint32_t n) {
    char b[10]; unsigned i = 0;
    do { b[i++] = (char)('0' + n % 10); n /= 10; } while (n);
    while (i) { char c[2] = {b[--i], 0}; uart_text(c); }
}
static void adc_init(void) {
    GPIOA_CRL &= ~15u; /* PA0 analog input */
    ADC_SMPR2 = 7; /* channel 0: 239.5 ADC cycles */
    ADC_SQR1 = 0; ADC_SQR3 = 0;
    ADC_CR2 = 1; delay_ms(2);
    ADC_CR2 |= 1u << 3; while (ADC_CR2 & (1u << 3)) {}
    ADC_CR2 |= 1u << 2; while (ADC_CR2 & (1u << 2)) {}
    ADC_CR2 |= (7u << 17) | (1u << 20); /* software trigger */
}
static uint32_t adc_read(void) {
    ADC_CR2 |= 1u << 22;
    while (!(ADC_SR & 2u)) {}
    return ADC_DR & 4095u;
}
int main(void) {
    RCC_CR |= 1; while (!(RCC_CR & 2u)) {}
    RCC_CFGR = 0; while (RCC_CFGR & 12u) {}
    RCC_APB2ENR |= (1u << 2) | (1u << 9) | (1u << 14);
    /* PA9 alternate function push-pull 2 MHz; PA10 floating input */
    GPIOA_CRH = (GPIOA_CRH & ~0xff0u) | 0x4a0u;
    USART_BRR = 69; /* 8 MHz / 115200, rounded */
    USART_CR1 = (1u << 13) | (1u << 3);
    if (!DEMO_MODE) adc_init();
    uint32_t sequence = 0;
    for (;;) {
        uint32_t raw = DEMO_MODE ? (sequence % 4096u) : adc_read();
        uint32_t mv = (raw * VREF_MV + 2047u) / 4095u;
        uart_text("DEVICE_DATA,ID="); uart_uint(sequence++);
        uart_text(",VALUE="); uart_uint(mv / 1000u); uart_text(".");
        if (mv % 1000u < 100u) uart_text("0");
        if (mv % 1000u < 10u) uart_text("0");
        uart_uint(mv % 1000u); uart_text("\r\n");
        delay_ms(100);
    }
}
