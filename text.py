import os
import shutil
import time
from datetime import datetime

# BIOS Settings
bios_settings = {
    "Computer Name": "MyPC",
    "CPU": "Intel Pentium III Processor 700MHz",
    "System RAM": "640K",
    "Extended RAM": "3072K",
    "Hard Disk": "10 GB",
}

# 模拟 BIOS 启动过程
def bios_startup():
    print("PhoenixBIOS 4.0 Release 6.0.3")
    time.sleep(0.5)
    print("Copyright 1985-2001 Phoenix Technologies Ltd.")
    time.sleep(0.5)
    print("All Rights Reserved")
    time.sleep(0.5)
    print("System Configuration:")
    time.sleep(0.5)
    for key, value in bios_settings.items():
        print(f"{key}: {value}")
    time.sleep(0.5)
    print("Detecting Primary Master... IDE Hard Disk 0: 10 GB")
    print("Detecting Secondary Master... ATAPI CD-ROM Drive")
    time.sleep(1)
    print("Mouse initialized")
    time.sleep(0.5)
    print(r"""
            ======================================
              ____   ____   _____    ____    _____
             |  _ \ / __ \ / ____|  / __ \  |  __ \
             | |_) | |  | | |      | |  | | | |  | |
             |  _ <| |  | | |      | |  | | | |  | |
             | |_) | |__| | |____  | |__| | | |__| |
             |____/ \____/ \_____|  \____/  |_____/

             Python DOS System v1.0
            ======================================
            """)
# DOS启动屏幕
def show_logo():
    bios_startup()
    print("\nMicrosoft(R) MS-DOS(R) Version 6.22\n(C)Copyright Microsoft Corp 1981-1994.\n")
    time.sleep(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_time():
    print("Current time:", datetime.now().strftime('%H:%M:%S'))

def show_date():
    print("Current date:", datetime.now().strftime('%Y-%m-%d'))

def disk_usage():
    total, used, free = shutil.disk_usage(".")
    print("Disk usage:")
    print(f"Total: {total // (1024 ** 3)} GB")
    print(f"Used: {used // (1024 ** 3)} GB")
    print(f"Free: {free // (1024 ** 3)} GB")

def format_disk():
    confirm = input("WARNING: Formatting will erase all data. Type 'yes' to continue: ")
    if confirm.lower() == "yes":
        for item in os.listdir():
            if os.path.isfile(item):
                os.remove(item)
            else:
                shutil.rmtree(item)
        print("Disk formatted successfully.")
    else:
        print("Format cancelled.")

def rename_file(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print(f"{old_name} renamed to {new_name}")
    except FileNotFoundError:
        print(f"File not found: {old_name}")
    except Exception as e:
        print(f"Error renaming file: {e}")

def calculator():
    print("Simple calculator: Enter a basic math expression (e.g., 2 + 3) or 'exit' to quit")
    while True:
        expr = input("Calc> ")
        if expr.lower() == 'exit':
            break
        try:
            result = eval(expr, {"__builtins__": {}})
            print("Result:", result)
        except Exception:
            print("Invalid expression")

def ping():
    print("Pinging 8.8.8.8 with 32 bytes of data:")
    for i in range(4):
        time.sleep(1)
        print("Reply from 8.8.8.8: bytes=32 time=48ms TTL=117")

def find_in_files(search_text):
    print(f"Searching for '{search_text}' in files...")
    for filename in os.listdir():
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                content = f.read()
                if search_text in content:
                    print(f"Text found in {filename}")
    print("Search completed.")

def run_batch_script(script_name):
    try:
        with open(script_name, 'r') as f:
            print(f"Running batch script: {script_name}")
            for line in f:
                command = line.strip()
                if command:
                    print(f"> {command}")
                    dos_command(command)
    except FileNotFoundError:
        print(f"Batch script not found: {script_name}")

def sysinfo():
    print("\nSystem Information:")
    for key, value in bios_settings.items():
        print(f"{key}: {value}")
    print("Operating System: MS-DOS 6.22\n")

def compress_file(file):
    if not os.path.isfile(file):
        print(f"{file} is not a valid file.")
        return
    try:
        shutil.make_archive(file, 'zip', root_dir=os.path.dirname(file), base_dir=file)
        print(f"File '{file}' compressed to '{file}.zip'")
    except Exception as e:
        print(f"Compression failed: {e}")

def extract_file(zip_file):
    if not zip_file.endswith('.zip'):
        print(f"{zip_file} is not a valid zip file.")
        return
    try:
        shutil.unpack_archive(zip_file, os.path.splitext(zip_file)[0])
        print(f"File '{zip_file}' extracted.")
    except FileNotFoundError:
        print(f"File not found: {zip_file}")
    except Exception as e:
        print(f"Extraction failed: {e}")

def dos_command(command_line):
    command = command_line.strip().split()
    if len(command) == 0:
        return
    elif command[0].lower() == "dir":
        list_directory()
    elif command[0].lower() == "cd":
        if len(command) > 1:
            change_directory(command[1])
        else:
            print("Please specify a directory")
    elif command[0].lower() == "mkdir":
        if len(command) > 1:
            make_directory(command[1])
        else:
            print("Please specify a directory name")
    elif command[0].lower() == "del":
        if len(command) > 1:
            delete_file(command[1])
        else:
            print("Please specify a file name")
    elif command[0].lower() == "time":
        show_time()
    elif command[0].lower() == "date":
        show_date()
    elif command[0].lower() == "disk":
        disk_usage()
    elif command[0].lower() == "format":
        format_disk()
    elif command[0].lower() == "rename":
        if len(command) > 2:
            rename_file(command[1], command[2])
        else:
            print("Please specify the old name and new name")
    elif command[0].lower() == "calc":
        calculator()
    elif command[0].lower() == "ping":
        ping()
    elif command[0].lower() == "cls":
        clear_screen()
    elif command[0].lower() == "find":
        if len(command) > 1:
            find_in_files(command[1])
        else:
            print("Please specify text to find")
    elif command[0].lower() == "batch":
        if len(command) > 1:
            run_batch_script(command[1])
        else:
            print("Please specify a batch file name")
    elif command[0].lower() == "sysinfo":
        sysinfo()
    elif command[0].lower() == "compress":
        if len(command) > 1:
            compress_file(command[1])
        else:
            print("Please specify a file to compress")
    elif command[0].lower() == "extract":
        if len(command) > 1:
            extract_file(command[1])
        else:
            print("Please specify a file to extract")
    elif command[0].lower() == "exit":
        print("Exiting program")
        return True
    else:
        print(f"'{command[0]}' is not recognized as an internal or external command, operable program, or batch file.")

def dos_simulation():
    show_logo()
    print("Type 'help' for a list of available commands.")
    while True:
        command_line = input(f"{os.getcwd()}> ")
        if dos_command(command_line):
            break

# Run the program
dos_simulation()
