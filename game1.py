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
        logging.info(f"已删除: {file_path}")
        return True
    except Exception as e:
        logging.error(f"删除 {file_path} 失败: {e}")
        return False


def backup_file(file_path):
    """备份文件到备份目录"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    shutil.copy(file_path, BACKUP_DIR)
    logging.info(f"已备份: {file_path}")


def zip_file(file_path):
    """压缩文件并返回压缩文件路径"""
    zip_file_path = f"{file_path}.zip"
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    return zip_file_path


def clean_directory(directory, to_recycle_bin, junk_extensions, backup, progress_callback):
    """清理指定目录中的垃圾文件"""
    total_deleted = 0
    total_freed_space = 0
    files_to_delete = []

    for root, _, files in os.walk(directory):
        for file in files:
            if is_junk_file(file, junk_extensions) and not is_excluded_file(file):
                file_path = os.path.join(root, file)
                files_to_delete.append(file_path)

    total_files = len(files_to_delete)

    for index, file_path in enumerate(files_to_delete):
        if backup:
            backup_file(file_path)
        compress = messagebox.askyesno("压缩文件", f"您要在删除 {file_path} 之前压缩它吗？")
        if compress:
            zip_file(file_path)
        total_freed_space += os.path.getsize(file_path)
        if delete_file(file_path, to_recycle_bin):
            total_deleted += 1

        # 更新进度
        progress_callback(total_deleted, total_files)

    return total_deleted, total_freed_space


def clean_cache(directory, to_recycle_bin, junk_extensions, backup, progress_callback):
    """清理缓存并统计信息"""
    total_deleted, freed_space = clean_directory(directory, to_recycle_bin, junk_extensions, backup, progress_callback)
    cleanup_history.append((time.strftime("%Y-%m-%d %H:%M:%S"), total_deleted, freed_space))
    messagebox.showinfo("清理总结", f"已删除文件总数: {total_deleted}, 释放空间: {freed_space / (1024 * 1024):.2f} MB")


def run_cleaning_thread(directory, to_recycle_bin, junk_extensions, backup):
    """在后台线程中执行清理"""
    clean_cache(directory, to_recycle_bin, junk_extensions, backup, update_progress)


def update_progress(deleted, total):
    """更新进度条"""
    progress_var.set(deleted / total * 100 if total > 0 else 0)


def start_cleanup():
    """开始清理的按钮回调函数"""
    password = simpledialog.askstring("密码", "请输入密码以继续:")
    if password == "gy09ss13":
        directory = simpledialog.askstring("目录", "请输入要清理的目录:")
        if directory and os.path.exists(directory):
            to_recycle_bin = messagebox.askyesno("回收站", "将文件移动到回收站而不是删除？")
            backup = messagebox.askyesno("备份", "您想在删除之前备份文件吗？")
            junk_extensions = simpledialog.askstring("自定义扩展名", "输入自定义垃圾文件扩展名（以逗号分隔）:")
            junk_extensions = [ext.strip() for ext in
                               junk_extensions.split(",")] if junk_extensions else DEFAULT_JUNK_EXTENSIONS

            threading.Thread(target=run_cleaning_thread, args=(directory, to_recycle_bin, junk_extensions, backup),
                             daemon=True).start()
            messagebox.showinfo("清理", "清理操作已在后台开始。")
        else:
            messagebox.showwarning("警告", "无效的目录！")
    else:
        messagebox.showwarning("警告", "密码错误！")


def create_gui():
    """创建 GUI 界面"""
    global progress_var
    root = tk.Tk()
    root.title("系统垃圾清理器")

    tk.Label(root, text="欢迎使用系统垃圾清理器").pack(pady=10)
    tk.Button(root, text="立即清理", command=start_cleanup).pack(pady=20)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, fill=tk.X)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
