import os
import subprocess
import configparser
import curses
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

CONFIG_FILE = 'build.conf'
PATCH_DIR = 'patch'

DEFAULT_CONFIG = {
    'kernel_src': 'src/kernel/main.c',
    'kernel_obj': 'kernel.o',
    'iso_dir': 'iso',
    'grub_cfg_dir': 'boot/grub',
    'grub_cfg': 'boot/grub/grub.cfg',
    'kernel_elf': 'iso/boot/kernel.elf',
    'linker_script': 'src/linker.ld',
    'iso_file': 'rawberry.iso',
    'cc': 'gcc',
    'ld': 'ld',
    'cflags': '-ffreestanding -m64 -g -nostdlib -nostartfiles -nodefaultlibs -mno-sse -mno-sse2 -mno-avx',
    'ldflags': '-nostdlib -T src/linker.ld',
    'grub_mkrescue': 'grub-mkrescue'
}

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config['DEFAULT'] = DEFAULT_CONFIG
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(CONFIG_FILE)
    return config['DEFAULT']

def save_config(config):
    parser = configparser.ConfigParser()
    parser['DEFAULT'] = config
    with open(CONFIG_FILE, 'w') as configfile:
        parser.write(configfile)

def curses_menu(stdscr, config):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    
    menu_items = list(config.keys()) + ["Zastosuj patch"]
    current_row = 0

    def print_menu():
        stdscr.clear()
        stdscr.addstr(0, 0, "Użyj strzałek, aby poruszać się po menu. ENTER, aby edytować.", curses.A_BOLD)
        for idx, item in enumerate(menu_items):
            if idx == current_row:
                stdscr.addstr(idx + 1, 0, f"> {item}: {config.get(item, '')}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f"  {item}: {config.get(item, '')}")
        stdscr.refresh()

    while True:
        print_menu()
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == ord('\n'):
            if current_row < len(config.keys()):
                stdscr.clear()
                stdscr.addstr(0, 0, f"Edytujesz: {menu_items[current_row]}")
                stdscr.addstr(1, 0, "Nowa wartość: ")
                curses.echo()
                new_value = stdscr.getstr(1, 13).decode('utf-8')
                config[menu_items[current_row]] = new_value
                save_config(config)
                curses.noecho()
            else:
                apply_patch_menu(stdscr)
        elif key == ord('q'):
            break

def build_project(config):
    print(Fore.GREEN + Style.BRIGHT + "Rozpoczynam budowanie projektu...")

    try:
        subprocess.run([config['cc'], *config['cflags'].split(), '-c', config['kernel_src'], '-o', config['kernel_obj']], check=True)
        print(Fore.YELLOW + f"Skopilowano {config['kernel_src']} do {config['kernel_obj']}")

        os.makedirs(os.path.join(config['iso_dir'], 'boot'), exist_ok=True)
        subprocess.run([config['ld'], *config['ldflags'].split(), '-o', config['kernel_elf'], config['kernel_obj']], check=True)
        print(Fore.YELLOW + f"Linkowano {config['kernel_obj']} do {config['kernel_elf']}")

        os.makedirs(os.path.join(config['iso_dir'], config['grub_cfg_dir']), exist_ok=True)
        subprocess.run(['cp', config['grub_cfg'], os.path.join(config['iso_dir'], config['grub_cfg_dir'])], check=True)
        subprocess.run([config['grub_mkrescue'], '-o', config['iso_file'], config['iso_dir']], check=True)
        print(Fore.CYAN + f"Utworzono ISO {config['iso_file']}")

        print(Fore.GREEN + Style.BRIGHT + "Budowanie zakończone sukcesem!")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "Błąd podczas budowania projektu!")
        print(Fore.RED + str(e))

def apply_patch_menu(stdscr):
    patches = [f for f in os.listdir(PATCH_DIR) if f.endswith('.patch')]
    if not patches:
        stdscr.clear()
        stdscr.addstr(0, 0, "Brak plików patch w folderze patch.")
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Wybierz patch do zastosowania i wciśnij ENTER.", curses.A_BOLD)
        for idx, patch in enumerate(patches):
            if idx == current_row:
                stdscr.addstr(idx + 1, 0, f"> {patch}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f"  {patch}")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(patches) - 1:
            current_row += 1
        elif key == ord('\n'): 
            patch_file = os.path.join(PATCH_DIR, patches[current_row])
            apply_patch(patch_file)
            break
        elif key == ord('q'):
            break

def apply_patch(patch_file):
    print(Fore.CYAN + f"Zastosowanie patcha: {patch_file}")
    try:
        subprocess.run(['patch', '-p1', '<', patch_file], check=True, shell=True)
        print(Fore.GREEN + "Patch zastosowany pomyślnie!")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "Błąd podczas stosowania patcha!")
        print(Fore.RED + str(e))

parser = argparse.ArgumentParser(description="Build system z obsługą curses i kolorów.")
parser.add_argument('-c', '--config', action='store_true', help="Edycja konfiguracji")
parser.add_argument('-b', '--build', action='store_true', help="Budowanie projektu")
args = parser.parse_args()

config = load_config()

if args.config:
    curses.wrapper(curses_menu, config)
elif args.build:
    build_project(config)
