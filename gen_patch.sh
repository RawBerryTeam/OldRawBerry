#!/bin/bash

PATCH_DIR="patch"

if [ ! -d "$PATCH_DIR" ]; then
    mkdir -p "$PATCH_DIR"
    echo "Utworzono katalog $PATCH_DIR"
fi

usage() {
    echo "Użycie: $0 -o <oryginalny_plik> -m <zmodyfikowany_plik> -n <nazwa_patcha>"
    echo ""
    echo "-o    Oryginalny plik wraz ze ścieżką (np. src/kernel/driver/ps.c)."
    echo "-m    Zmodyfikowany plik wraz ze ścieżką (np. src/kernel/driver/ps_mod.c)."
    echo "-n    Nazwa pliku .patch, który zostanie zapisany w folderze $PATCH_DIR."
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
            echo "Nieznana opcja: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Opcja -$OPTARG wymaga argumentu." >&2
            usage
            ;;
    esac
done

if [ -z "$ORIGINAL_FILE" ] || [ -z "$MODIFIED_FILE" ] || [ -z "$PATCH_NAME" ]; then
    echo "Błąd: Wszystkie argumenty -o, -m i -n są wymagane."
    usage
fi

PATCH_PATH="$PATCH_DIR/$PATCH_NAME.patch"

echo "Generowanie patcha z $ORIGINAL_FILE i $MODIFIED_FILE..."
diff -u "$ORIGINAL_FILE" "$MODIFIED_FILE" > "$PATCH_PATH"

if [ $? -eq 0 ]; then
    echo "Patch zapisany jako $PATCH_PATH"
else
    echo "Błąd podczas generowania patcha!"
fi
