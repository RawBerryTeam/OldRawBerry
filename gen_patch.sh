#!/bin/bash

PATCH_DIR="patch"

if [ ! -d "$PATCH_DIR" ]; then
    mkdir -p "$PATCH_DIR"
    echo "Created directory $PATCH_DIR"
fi

usage() {
    echo "Usage: $0 -o <original_file> -m <modified_file> -n <patch_name>"
    echo ""
    echo "-o    Original file with path (e.g., src/kernel/driver/ps.c)."
    echo "-m    Modified file with path (e.g., src/kernel/driver/ps_mod.c)."
    echo "-n    Name of the .patch file that will be saved in the $PATCH_DIR folder."
    echo ""
    exit 1
}

while getopts ":o:m:n:" opt; do
    case $opt in
        o) 
            ORIGINAL_FILE="$OPTARG"
            ;;
        m)
            MODIFIED_FILE="$OPTARG"
            ;;
        n)
            PATCH_NAME="$OPTARG"
            ;;
        \?)
            echo "Unknown option: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
    esac
done

if [ -z "$ORIGINAL_FILE" ] || [ -z "$MODIFIED_FILE" ] || [ -z "$PATCH_NAME" ]; then
    echo "Error: All options -o, -m, and -n are required."
    usage
fi

PATCH_PATH="$PATCH_DIR/$PATCH_NAME.patch"

echo "Generating patch from $ORIGINAL_FILE and $MODIFIED_FILE..."
diff -u "$ORIGINAL_FILE" "$MODIFIED_FILE" > "$PATCH_PATH"
