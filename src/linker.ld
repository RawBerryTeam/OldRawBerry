OUTPUT_FORMAT(elf32-i386)
ENTRY(kernel_main)

SECTIONS
{
    . = 0x100000;
    .text : {
        *(.text)
    }
    .data : {
        *(.data)
    }
    .bss : {
        *(.bss)
        *(COMMON)
    }
}