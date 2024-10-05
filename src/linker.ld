OUTPUT_FORMAT("elf64-x86-64")
ENTRY(kernel_main)

SECTIONS
{
    .text : {
        *(.text)
    } > KERNEL

    .rodata : {
        *(.rodata)
    } > KERNEL

    .data : {
        *(.data)
    } > KERNEL
}