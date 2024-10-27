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

# Simulate BIOS and DOS boot process
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
# DOS startup screen
def show_logo():
    bios_startup()
    print("\nMicrosoft(R) MS-DOS(R) Version 6.22\n(C)Copyright Microsoft Corp 1981-1994.\n")
    time.sleep(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_directory():
    print(" Volume in drive C has no label")
    print(" Volume Serial Number is 1234-5678\n")
    print(" Directory of", os.getcwd(), "\n")
    for item in os.listdir():
        file_time = datetime.fromtimestamp(os.path.getmtime(item)).strftime('%m-%d-%y  %I:%M %p')
        if os.path.isdir(item):
            print(f"{file_time}    <DIR>          {item}")
        else:
            size = os.path.getsize(item)
            print(f"{file_time}           {size:>10} {item}")
    print("               0 bytes free\n")

def change_directory(directory):
    try:
        os.chdir(directory)
        print(f"Current directory is {os.getcwd()}")
    except FileNotFoundError:
        print(f"The system cannot find the path specified: {directory}")
    except NotADirectoryError:
        print(f"{directory} is not a directory")

def make_directory(directory):
    try:
        os.mkdir(directory)
        print(f"Directory created: {directory}")
    except FileExistsError:
        print(f"A subdirectory or file {directory} already exists")

def delete_file(file):
    try:
        os.remove(file)
        print(f"{file} deleted")
    except FileNotFoundError:
        print(f"File not found: {file}")
    except IsADirectoryError:
        print(f"{file} is a directory")

def type_file(file):
    try:
        with open(file, 'r') as f:
            print(f.read())
    except FileNotFoundError:
        print(f"File not found: {file}")
    except IsADirectoryError:
        print(f"{file} is a directory")
    except Exception as e:
        print(f"Error reading file: {e}")

def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
        print(f"{src} copied to {dst}")
    except FileNotFoundError:
        print(f"File not found: {src}")
    except Exception as e:
        print(f"Copy error: {e}")

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        print(f"{src} moved to {dst}")
    except FileNotFoundError:
        print(f"File or directory not found: {src}")
    except Exception as e:
        print(f"Move error: {e}")

def edit_file(file):
    print(f"Editing file: {file}")
    print("Enter your text (type 'exit' on a new line to save and exit):")
    lines = []
    while True:
        line = input()
        if line.lower() == "exit":
            break
        lines.append(line)
    with open(file, 'w') as f:
        f.write("\n".join(lines))
    print(f"File '{file}' saved.")

def open_file(file):
    try:
        with open(file, 'r') as f:
            print(f"\nContents of {file}:\n")
            print(f.read())
    except FileNotFoundError:
        print(f"File not found: {file}")
    except IsADirectoryError:
        print(f"{file} is a directory")
    except Exception as e:
        print(f"Error opening file: {e}")

def run_executable(file):
    if not file.endswith('.exe'):
        print(f"{file} is not a valid executable.")
        return
    try:
        print(f"Running {file}...")
        time.sleep(1)  # Simulate some processing time
        print(f"{file} executed successfully!")
    except Exception as e:
        print(f"Error executing file: {e}")

def modify_bios_settings():
    global bios_settings
    print("\nCurrent BIOS Settings:")
    for key, value in bios_settings.items():
        print(f"{key}: {value}")

    while True:
        setting = input("\nEnter the setting name to modify (or type 'exit' to return): ").strip()
        if setting.lower() == "exit":
            break
        elif setting in bios_settings:
            new_value = input(f"Enter new value for {setting}: ").strip()
            bios_settings[setting] = new_value
            print(f"{setting} updated to {new_value}")
        else:
            print(f"{setting} is not a valid setting.")

def dos_simulation():
    show_logo()
    print("Type 'help' for a list of available commands.")

    while True:
        command = input(f"{os.getcwd()}> ").strip().split()

        if len(command) == 0:
            continue
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
        elif command[0].lower() == "type":
            if len(command) > 1:
                type_file(command[1])
            else:
                print("Please specify a file name")
        elif command[0].lower() == "copy":
            if len(command) > 2:
                copy_file(command[1], command[2])
            else:
                print("Please specify the source file and destination path")
        elif command[0].lower() == "move":
            if len(command) > 2:
                move_file(command[1], command[2])
            else:
                print("Please specify the source file and destination path")
        elif command[0].lower() == "cls":
            clear_screen()
        elif command[0].lower() == "exit":
            print("Exiting program")
            break
        elif command[0].lower() == "help":
            print("""
            Available commands:
            - dir : List files and folders in the current directory
            - cd <directory> : Change to the specified directory
            - mkdir <directory> : Create a new directory
            - del <file> : Delete a file
            - type <file> : Display the contents of a file
            - copy <src> <dst> : Copy a file
            - move <src> <dst> : Move a file
            - cls : Clear the screen
            - exit : Exit the program
            - edit <file> : Edit a file
            - open <file> : Open a file
            - run <file> : Run an executable file
            - bios : Modify BIOS settings
            """)
        elif command[0].lower() == "edit":
            if len(command) > 1:
                edit_file(command[1])
            else:
                print("Please specify a file name to edit")
        elif command[0].lower() == "open":
            if len(command) > 1:
                open_file(command[1])
            else:
                print("Please specify a file name to open")
        elif command[0].lower() == "run":
            if len(command) > 1:
                run_executable(command[1])
            else:
                print("Please specify an executable file to run")
        elif command[0].lower() == "bios":
            modify_bios_settings()
        else:
            print(f"'{command[0]}' is not recognized as an internal or external command, operable program, or batch file.")

# Run the program
dos_simulation()