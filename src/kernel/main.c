#include <stdint.h>
#include "main.h"
#include "drivers/ports.h"

void print_string(const char* str);
void kernel_main(void);
void panic(const char* message);

void print_string(const char* str) {
    uint16_t* vga_buffer = (uint16_t*)VGA_BUFFER;
    while (*str) {
        *vga_buffer = (uint16_t)(*str | 0x0F00); 
        vga_buffer++;
        str++;
    }
    *vga_buffer = (uint16_t)('\n' | 0x0F00);
}

void kernel_main() {
    print_string("Hello RawBerry");
    while (1) {}
}

void panic(const char* message) {
    while (1) {}
}
