#include <stdint.h>
#include "main.h"

void print_string(const char* str);
void kernel_main(void);
void panic(const char* message)

void print_string(const char* str) {
    uint16_t* vga_buffer = (uint16_t*)VGA_BUFFER;
    while (*str) {
        *vga_buffer = (uint16_t)(*str | 0x0F00); 
        vga_buffer++;
        str++;
    }
}

void kernel_main() {
    print_string("Hello RawBerry");
    print_string("This is version 0.1.1 of this kernel!")
}

void panic(const char* message) {
    while (1) {}
}
