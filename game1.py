import os
import shutil
import tempfile
import psutil
import time
import json
from send2trash import send2trash
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, Listbox, Scrollbar

# 默认备份路径
DEFAULT_BACKUP_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "Backup")


# 记录日志的函数
def log_action(action):
    with open("cleanup_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")


# 清理临时文件夹
def clear_temp_folder(backup_folder):
    temp_folder = tempfile.gettempdir()
    deleted_files = []
    try:
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                # 先备份到指定文件夹
                shutil.move(file_path, backup_folder)
                deleted_files.append(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 直接删除文件夹
        log_action(f"清理临时文件夹: {deleted_files}")
        return deleted_files
    except Exception as e:
        print(f"清理时出错: {e}")
        return []


# 清理下载文件夹中的旧文件
def clear_download_folder(backup_folder, days=100):
    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    now = time.time()
    deleted_files = []
    for filename in os.listdir(download_folder):
        file_path = os.path.join(download_folder, filename)
        if os.path.isfile(file_path) and (now - os.path.getmtime(file_path)) > days * 86400:
            # 先备份到指定文件夹
            shutil.move(file_path, backup_folder)
            deleted_files.append(file_path)
    log_action(f"下载文件夹清理（超过{days}天的文件）: {deleted_files}")
    return deleted_files


# 从备份恢复文件
def restore_files_from_backup(backup_folder, files_to_restore):
    restored_files = []
    for file_name in files_to_restore:
        source = os.path.join(backup_folder, file_name)
        destination = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
        try:
            shutil.move(source, destination)  # 移动到下载文件夹
            log_action(f"恢复文件: {file_name}")
            restored_files.append(file_name)
        except Exception as e:
            print(f"恢复文件时出错: {e}")
    return restored_files


# 读取配置文件
def read_config():
    try:
        with open("cleanup_config.json", "r") as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        print("配置文件未找到，使用默认设置。")
        return {}


# 保存配置文件
def save_config(backup_folder):
    config = {"backup_folder": backup_folder}
    with open("cleanup_config.json", "w") as config_file:
        json.dump(config, config_file)


# GUI 类
class CleanupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("系统清理工具")

        self.config = read_config()
        self.backup_folder = self.config.get("backup_folder", DEFAULT_BACKUP_FOLDER)

        # 创建备份路径输入框
        self.backup_label = tk.Label(root, text="备份文件夹路径:")
        self.backup_label.pack()

        self.backup_entry = tk.Entry(root, width=50)
        self.backup_entry.insert(0, self.backup_folder)
        self.backup_entry.pack()

        self.browse_button = tk.Button(root, text="选择备份文件夹", command=self.browse_backup_folder)
        self.browse_button.pack()

        # 清理按钮
        self.clean_temp_button = tk.Button(root, text="清理临时文件夹", command=self.clean_temp_folder)
        self.clean_temp_button.pack()

        self.clean_download_button = tk.Button(root, text="清理下载文件夹中超过100天的旧文件",
                                               command=self.clean_download_folder)
        self.clean_download_button.pack()

        # 恢复文件按钮
        self.restore_button = tk.Button(root, text="恢复文件", command=self.restore_files)
        self.restore_button.pack()

        # 文件列表框
        self.file_list = Listbox(root, selectmode='multiple', height=10)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.file_list.yview)

        # 保存设置按钮
        self.save_button = tk.Button(root, text="保存备份路径设置", command=self.save_settings)
        self.save_button.pack()

    def browse_backup_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, folder_selected)

    def clean_temp_folder(self):
        deleted_files = clear_temp_folder(self.backup_entry.get())
        if deleted_files:
            messagebox.showinfo("清理完成", f"清理了以下临时文件:\n{', '.join(deleted_files)}")
        else:
            messagebox.showinfo("清理完成", "临时文件夹没有清理任何文件。")

    def clean_download_folder(self):
        deleted_files = clear_download_folder(self.backup_entry.get())
        if deleted_files:
            messagebox.showinfo("清理完成", f"清理了以下过期下载文件:\n{', '.join(deleted_files)}")
        else:
            messagebox.showinfo("清理完成", "下载文件夹没有清理任何文件。")

    def restore_files(self):
        selected_files = self.file_list.curselection()
        files_to_restore = [self.file_list.get(i) for i in selected_files]
        restored_files = restore_files_from_backup(self.backup_entry.get(), files_to_restore)
        if restored_files:
            messagebox.showinfo("恢复完成", f"已恢复文件:\n{', '.join(restored_files)}")
        else:
            messagebox.showinfo("恢复完成", "没有文件被恢复。")
        self.update_file_list()

    def update_file_list(self):
        self.file_list.delete(0, tk.END)
        backup_files = os.listdir(self.backup_entry.get())
        for file_name in backup_files:
            self.file_list.insert(tk.END, file_name)

    def save_settings(self):
        save_config(self.backup_entry.get())
        messagebox.showinfo("保存设置", "备份路径设置已保存。")


# 运行主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = CleanupApp(root)
    root.mainloop()