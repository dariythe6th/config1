import os
import logging
import tarfile
import tkinter as tk
from tkinter import scrolledtext, filedialog
from pathlib import Path
import zipfile
import configparser

# Set up logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(message)s')

def log_action(action):
    logging.info(action)

def list_directory(path=None):
    try:
        path = path or os.getcwd()
        entries = os.listdir(path)
        output = "\n".join(entries)
        return output
    except FileNotFoundError:
        return "Directory not found."
    except OSError as e:
        return f"Error accessing directory: {e}"

def change_directory(path):
    try:
        new_path = os.path.join(os.getcwd(), path)  # Correct path joining
        os.chdir(new_path)
        return f"Changed directory to: {os.getcwd()}"
    except FileNotFoundError:
        return "Directory not found."
    except OSError as e:
        return f"Error changing directory: {e}"

def cat_command(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:  # Указание кодировки
            return file.read()
    except FileNotFoundError:
        return "File not found."
    except UnicodeDecodeError:
        return "Error decoding file: ensure it is in UTF-8 format."
    except OSError as e:
        return f"Error reading file: {e}"

def tail_command(filepath, lines=5):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:  # Указание кодировки
            content = file.readlines()
            return ''.join(content[-lines:])
    except FileNotFoundError:
        return "File not found."
    except UnicodeDecodeError:
        return "Error decoding file: ensure it is in UTF-8 format."
    except OSError as e:
        return f"Error reading file: {e}"


def clear_command():
    output_box.configure(state='normal')
    output_box.delete('1.0', tk.END)
    output_box.configure(state='disabled')
    return "Console cleared."

def process_command(command):
    log_action(command)
    parts = command.split()
    command_name = parts[0]

    try:
        if command_name == "exit":
            app.quit()
        elif command_name == "ls":
            if len(parts) > 1:
                return list_directory(parts[1])  # Handles ls <directory>
            else:
                return list_directory()
        elif command_name == "cd":
            if len(parts) > 1:
                return change_directory(parts[1])
            else:
                return "cd requires a directory argument."
        elif command_name == "cat":
            if len(parts) > 1:
                return cat_command(parts[1])
            else:
                return "cat requires a file argument."
        elif command_name == "tail":
            if len(parts) > 1:
                lines = int(parts[2]) if len(parts) > 2 else 10
                return tail_command(parts[1], lines)
            else:
                return "tail requires a file argument."
        elif command_name == "clear":
            return clear_command()
        else:
            return "Command not recognized."
    except Exception as e:
        return f"An error occurred: {e}"

def on_enter(event):
    command = entry.get()
    entry.delete(0, tk.END)
    result = process_command(command)
    output_box.configure(state='normal')
    output_box.insert(tk.END, f"{Path.cwd()}/:> {command}\n{result}\n")
    output_box.configure(state='disabled')
    output_box.see(tk.END)

def load_vfs():
    config['DEFAULT']['vfs_path'] = filedialog.askopenfilename(filetypes=[("Tar files", "*.tar")])
    if config['DEFAULT']['vfs_path']:
        try:
            with tarfile.TarFile(config['DEFAULT']['vfs_path'], 'r') as tar_ref:
                tar_ref.extractall("./vfs")
                os.chdir("./vfs")  # Change dir to the extracted vfs
                print(f"Virtual filesystem loaded from: {config['DEFAULT']['vfs_path']}")

        except FileNotFoundError:
            print("Error: Tar file not found.")
        except zipfile.BadZipFile:
            print("Error: Invalid tar file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# --- GUI setup ---
app = tk.Tk()
app.title("Linux Console Emulator")
app.geometry("800x600")

# Config file handling
config = configparser.ConfigParser()
config.read('config.ini')

# If no config file, create it with defaults
if not config.has_section('DEFAULT'):
    config['DEFAULT'] = {'computer_name': 'MyVirtualMachine', 'vfs_path': '', 'log_file': 'log.txt'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Menu
menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Load VFS", command=load_vfs)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=app.quit)
menubar.add_cascade(label="File", menu=filemenu)
app.config(menu=menubar)

# Output box
output_box = scrolledtext.ScrolledText(app, state='disabled', wrap=tk.WORD, height=20)
output_box.pack(fill=tk.BOTH, expand=True)

# Input field
entry = tk.Entry(app)
entry.pack(fill=tk.X)
entry.bind("<Return>", on_enter)

# Start the GUI
app.mainloop()
