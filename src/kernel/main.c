#include <stdint.h>
#include "main.h"

void print_string(const char* str);
void kernel_main(void);
void panic(const char* message);

void print_string(const char* str) {
    uint16_t* vga_buffer = (uint16_t*)0xB8000;
    int offset = 0;
    while (*str) {
        if (offset >= 80 * 25) {
            break;
        }
        vga_buffer[offset] = (*str & 0xFF) | (0x0F << 8);
        offset++;
        str++;
    }
    if (offset < 80 * 25) {
        vga_buffer[offset] = ('\n' & 0xFF) | (0x0F << 8);
    }
}

void kernel_main() {
    print_string("Hello RawBerry");
    while (1) {}
}

void panic(const char* message) {
    print_string("Panic");
    while (1) {}
}
