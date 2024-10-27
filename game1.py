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
        compress = messagebox.askyesno("压缩文件", f"您要在删除 {file_path} 之前压缩它吗？")
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
    messagebox.showinfo("清理总结", f"已删除文件总数: {total_deleted}, 释放空间: {freed_space / (1024 * 1024):.2f} MB")

def export_cleanup_history():
    """导出清理历史记录"""
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
    if file_path:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["日期", "删除的文件", "释放空间 (字节)"])
            for entry in cleanup_history:
                writer.writerow(entry)
        messagebox.showinfo("导出完成", f"清理历史已导出到 {file_path}")

def run_cleaning_thread(directory, to_recycle_bin, junk_extensions, backup):
    """在后台线程中执行清理"""
    clean_cache(directory, to_recycle_bin, junk_extensions, backup)

def on_clean():
    """清理按钮回调函数"""
    password = simpledialog.askstring("密码", "请输入密码以继续:")
    if password == "gy09ss13":  # 这里是更新后的密码
        directory = simpledialog.askstring("目录", "请输入要清理的目录:")
        if directory and os.path.exists(directory):
            to_recycle_bin = messagebox.askyesno("回收站", "将文件移动到回收站而不是删除？")
            backup = messagebox.askyesno("备份", "您想在删除之前备份文件吗？")
            junk_extensions = simpledialog.askstring("自定义扩展名", "输入自定义垃圾文件扩展名（以逗号分隔）:")
            junk_extensions = [ext.strip() for ext in junk_extensions.split(",")] if junk_extensions else DEFAULT_JUNK_EXTENSIONS
            
            threading.Thread(target=run_cleaning_thread, args=(directory, to_recycle_bin, junk_extensions, backup), daemon=True).start()
            messagebox.showinfo("清理", "清理操作已在后台开始。")
        else:
            messagebox.showwarning("警告", "无效的目录！")
    else:
        messagebox.showwarning("警告", "密码错误！")

def add_custom_extension():
    """添加自定义扩展名"""
    new_extension = simpledialog.askstring("自定义扩展名", "输入新的垃圾文件扩展名（例如 .temp）:")
    if new_extension:
        DEFAULT_JUNK_EXTENSIONS.append(new_extension)
        messagebox.showinfo("扩展名已添加", f"{new_extension} 已添加到垃圾文件扩展名列表中。")

def view_log():
    """查看日志文件"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            log_content = log_file.read()
        log_window = tk.Toplevel()
        log_window.title("日志文件")
        log_text = tk.Text(log_window)
        log_text.insert(tk.END, log_content)
        log_text.pack(expand=True, fill='both')
    else:
        messagebox.showwarning("警告", "日志文件不存在。")

def create_gui():
    """创建 GUI 界面"""
    root = tk.Tk()
    root.title("系统垃圾清理器")
    
    tk.Label(root, text="欢迎使用系统垃圾清理器").pack(pady=10)
    tk.Button(root, text="立即清理", command=on_clean).pack(pady=20)
    tk.Button(root, text="添加自定义扩展名", command=add_custom_extension).pack(pady=10)
    tk.Button(root, text="查看日志", command=view_log).pack(pady=10)
    tk.Button(root, text="导出清理历史", command=export_cleanup_history).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
