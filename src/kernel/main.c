#include <stdint.h>
#define MULTIBOOT_HEADER_MAGIC 0x1BADB002
#define MULTIBOOT_HEADER_FLAGS 0x00000003
#define MULTIBOOT_CHECKSUM -(MULTIBOOT_HEADER_MAGIC + MULTIBOOT_HEADER_FLAGS)

typedef struct {
    uint32_t magic;
    uint32_t flags;
    uint32_t checksum;
} multiboot_header_t __attribute__((packed));

multiboot_header_t multiboot_header __attribute__((section(".multiboot"))) = {
    .magic = MULTIBOOT_HEADER_MAGIC,
    .flags = MULTIBOOT_HEADER_FLAGS,
    .checksum = MULTIBOOT_CHECKSUM,
};

#define VGA_BUFFER 0xb8000

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
}

void panic(const char* message) {
    while (1) {}
}
