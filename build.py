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
    
    menu_items = list(config.keys()) + ["Apply patches", "Save and Exit", "Save and Build"]
    current_row = 0

    def print_menu():
        stdscr.clear()
        stdscr.addstr(0, 0, "Use arrows to navigate. Press ENTER to edit.", curses.A_BOLD)
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
                stdscr.addstr(0, 0, f"Editing: {menu_items[current_row]}")
                stdscr.addstr(1, 0, "New value: ")
                curses.echo()
                new_value = stdscr.getstr(1, 13).decode('utf-8')
                config[menu_items[current_row]] = new_value
                save_config(config)
                curses.noecho()
            elif menu_items[current_row] == "Apply patches":
                apply_patch_menu(stdscr)
            elif menu_items[current_row] == "Save and Exit":
                save_config(config)
                break
            elif menu_items[current_row] == "Save and Build":
                save_config(config)
                build_project(config)
                break
        elif key == ord('q'):
            break
        elif key == curses.KEY_LEFT: 
            break

def build_project(config):
    print(Fore.GREEN + Style.BRIGHT + "Starting project build...")

    try:
        subprocess.run([config['cc'], *config['cflags'].split(), '-c', config['kernel_src'], '-o', config['kernel_obj']], check=True)
        print(Fore.YELLOW + f"Compiled {config['kernel_src']} to {config['kernel_obj']}")

        os.makedirs(os.path.join(config['iso_dir'], 'boot'), exist_ok=True)
        subprocess.run([config['ld'], *config['ldflags'].split(), '-o', config['kernel_elf'], config['kernel_obj']], check=True)
        print(Fore.YELLOW + f"Linked {config['kernel_obj']} to {config['kernel_elf']}")

        os.makedirs(os.path.join(config['iso_dir'], config['grub_cfg_dir']), exist_ok=True)
        subprocess.run(['cp', config['grub_cfg'], os.path.join(config['iso_dir'], config['grub_cfg_dir'])], check=True)
        subprocess.run([config['grub_mkrescue'], '-o', config['iso_file'], config['iso_dir']], check=True)
        print(Fore.CYAN + f"Created ISO {config['iso_file']}")

        print(Fore.GREEN + Style.BRIGHT + "Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "Error during project build!")
        print(Fore.RED + str(e))

def apply_patch_menu(stdscr):
    patches = [f for f in os.listdir(PATCH_DIR) if f.endswith('.patch')]
    selected_patches = [False] * len(patches)

    if not patches:
        stdscr.clear()
        stdscr.addstr(0, 0, "No patch files in the patch folder.")
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select patches with X, then press Q to return.", curses.A_BOLD)
        for idx, patch in enumerate(patches):
            if idx == current_row:
                mark = "[*]" if selected_patches[idx] else "[ ]"
                stdscr.addstr(idx + 1, 0, f"> {mark} {patch}", curses.A_REVERSE)
            else:
                mark = "[*]" if selected_patches[idx] else "[ ]"
                stdscr.addstr(idx + 1, 0, f"  {mark} {patch}")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(patches) - 1:
            current_row += 1
        elif key == ord('x') or key == ord('X'):
            selected_patches[current_row] = not selected_patches[current_row]
        elif key == ord('q'):
            for idx, selected in enumerate(selected_patches):
                if selected:
                    apply_patch(os.path.join(PATCH_DIR, patches[idx]))
            break
        elif key == curses.KEY_LEFT: 
            break

def apply_patch(patch_file):
    print(Fore.CYAN + f"Applying patch: {patch_file}")
    try:
        subprocess.run(['patch', '-p1', '<', patch_file], check=True, shell=True)
        print(Fore.GREEN + "Patch applied successfully!")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "Error applying patch!")
        print(Fore.RED + str(e))

parser = argparse.ArgumentParser(description="Build system with curses and color support.")
parser.add_argument('-c', '--config', action='store_true', help="Edit configuration")
parser.add_argument('-b', '--build', action='store_true', help="Build the project")
args = parser.parse_args()

config = load_config()

if args.config:
    curses.wrapper(curses_menu, config)
elif args.build:
    build_project(config)
