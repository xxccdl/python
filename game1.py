import os
import time
import logging
import zipfile
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import csv
import shutil
import threading

# 垃圾文件扩展名
DEFAULT_JUNK_EXTENSIONS = [".tmp", ".log", ".bak", ".old", ".swp", ".DS_Store", "~", ".crdownload"]
# 自定义保留文件扩展名
DEFAULT_EXCLUDE_EXTENSIONS = [".pdf", ".docx"]
# 清理历史记录
cleanup_history = []
cleanup_interval = None  # 存储定时清理间隔
LOG_FILE = "cleanup_log.txt"  # 默认日志文件
BACKUP_DIR = "backup"  # 备份目录

# 配置日志
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def is_junk_file(file_name, junk_extensions):
    """检查文件是否为垃圾文件"""
    return any(file_name.endswith(ext) for ext in junk_extensions)

def is_excluded_file(file_name):
    """检查文件是否为保留文件"""
    return any(file_name.endswith(ext) for ext in DEFAULT_EXCLUDE_EXTENSIONS)

def delete_file(file_path, to_recycle_bin=False):
    """删除文件并记录日志"""
    try:
        if to_recycle_bin:
            recycle_bin = os.path.expanduser("~/.local/share/Trash/files")
            if not os.path.exists(recycle_bin):
                os.makedirs(recycle_bin)
            shutil.move(file_path, recycle_bin)
        else:
            os.remove(file_path)
        logging.info(f"Deleted: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to delete {file_path}: {e}")
        return False

def backup_file(file_path):
    """备份文件到备份目录"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    shutil.copy(file_path, BACKUP_DIR)
    logging.info(f"Backed up: {file_path}")

def zip_file(file_path):
    """压缩文件并返回压缩文件路径"""
    zip_file_path = f"{file_path}.zip"
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    return zip_file_path

def clean_directory(directory, to_recycle_bin, junk_extensions, backup):
    """清理指定目录中的垃圾文件"""
    total_deleted = 0
    total_freed_space = 0
    files_to_delete = []

    for root, _, files in os.walk(directory):
        for file in files:
            if is_junk_file(file, junk_extensions) and not is_excluded_file(file):
                file_path = os.path.join(root, file)
                files_to_delete.append(file_path)

    for file_path in files_to_delete:
        if backup:
            backup_file(file_path)
        compress = messagebox.askyesno("Compress File", f"Do you want to compress {file_path} before deleting?")
        if compress:
            zip_file(file_path)
        total_freed_space += os.path.getsize(file_path)
        if delete_file(file_path, to_recycle_bin):
            total_deleted += 1

    return total_deleted, total_freed_space

def clean_cache(directory, to_recycle_bin, junk_extensions, backup):
    """清理缓存并统计信息"""
    total_deleted, freed_space = clean_directory(directory, to_recycle_bin, junk_extensions, backup)
    cleanup_history.append((time.strftime("%Y-%m-%d %H:%M:%S"), total_deleted, freed_space))
    messagebox.showinfo("Cleanup Summary", f"Total files deleted: {total_deleted}, Freed space: {freed_space / (1024 * 1024):.2f} MB")

def export_cleanup_history():
    """导出清理历史记录"""
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Files Deleted", "Freed Space (bytes)"])
            for entry in cleanup_history:
                writer.writerow(entry)
        messagebox.showinfo("Export Complete", f"Cleanup history exported to {file_path}")

def run_cleaning_thread(directory, to_recycle_bin, junk_extensions, backup):
    """在后台线程中执行清理"""
    clean_cache(directory, to_recycle_bin, junk_extensions, backup)

def on_clean():
    """清理按钮回调函数"""
    password = simpledialog.askstring("Password", "Enter your password to proceed:")
    if password == "gy09ss13":  # 这里是更新后的密码
        directory = simpledialog.askstring("Directory", "Enter directory to clean:")
        if directory and os.path.exists(directory):
            to_recycle_bin = messagebox.askyesno("Recycle Bin", "Move files to Recycle Bin instead of deleting?")
            backup = messagebox.askyesno("Backup", "Do you want to backup the files before deletion?")
            junk_extensions = simpledialog.askstring("Custom Extensions", "Enter custom junk file extensions (comma separated):")
            junk_extensions = [ext.strip() for ext in junk_extensions.split(",")] if junk_extensions else DEFAULT_JUNK_EXTENSIONS
            
            threading.Thread(target=run_cleaning_thread, args=(directory, to_recycle_bin, junk_extensions, backup), daemon=True).start()
            messagebox.showinfo("Cleanup", "Cleanup started in the background.")
        else:
            messagebox.showwarning("Warning", "Invalid directory!")
    else:
        messagebox.showwarning("Warning", "Incorrect password!")

def add_custom_extension():
    """添加自定义扩展名"""
    new_extension = simpledialog.askstring("Custom Extension", "Enter a new junk file extension (e.g., .temp):")
    if new_extension:
        DEFAULT_JUNK_EXTENSIONS.append(new_extension)
        messagebox.showinfo("Extension Added", f"{new_extension} added to junk file extensions.")

def view_log():
    """查看日志文件"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            log_content = log_file.read()
        log_window = tk.Toplevel()
        log_window.title("Log File")
        log_text = tk.Text(log_window)
        log_text.insert(tk.END, log_content)
        log_text.pack(expand=True, fill='both')
    else:
        messagebox.showwarning("Warning", "Log file does not exist.")

def create_gui():
    """创建 GUI 界面"""
    root = tk.Tk()
    root.title("System Junk Cleaner")
    
    tk.Label(root, text="Welcome to the System Junk Cleaner").pack(pady=10)
    tk.Button(root, text="Clean Now", command=on_clean).pack(pady=20)
    tk.Button(root, text="Add Custom Extension", command=add_custom_extension).pack(pady=10)
    tk.Button(root, text="View Log", command=view_log).pack(pady=10)
    tk.Button(root, text="Export Cleanup History", command=export_cleanup_history).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
