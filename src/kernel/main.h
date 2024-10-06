#define MULTIBOOT_HEADER_MAGIC 0x1BADB002
#define MULTIBOOT_HEADER_FLAGS 0x00000003
#define MULTIBOOT_CHECKSUM -(MULTIBOOT_HEADER_MAGIC + MULTIBOOT_HEADER_FLAGS)

#define VGA_BUFFER 0xB8000

void kernel_main(void);
void panic(const char* message);

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