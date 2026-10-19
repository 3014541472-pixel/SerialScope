#include <stdint.h>
extern uint32_t _estack, _sidata, _sdata, _edata, _sbss, _ebss;
int main(void);
void Default_Handler(void) { for (;;) {} }
void Reset_Handler(void) {
    uint32_t *src = &_sidata;
    for (uint32_t *dst = &_sdata; dst < &_edata;) *dst++ = *src++;
    for (uint32_t *dst = &_sbss; dst < &_ebss;) *dst++ = 0;
    (void)main();
    for (;;) {}
}
typedef void (*handler)(void);
__attribute__((section(".isr_vector"), used))
const handler vectors[76] = {
    [0] = (handler)&_estack, [1] = Reset_Handler,
    [2 ... 75] = Default_Handler
};
