import os
import shutil
import tempfile
import psutil
import time
import json
import threading
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox, filedialog
import csv

# 配置文件和默认设置
CONFIG_FILE = "cleanup_config.json"
DEFAULT_BACKUP_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "Backup")
AUTO_CLEAN_INTERVAL = 7  # 默认每7天自动清理一次

# 读取配置文件
def read_config():
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        print("配置文件未找到，使用默认设置。")
        return {"backup_folder": DEFAULT_BACKUP_FOLDER, "clean_interval": AUTO_CLEAN_INTERVAL, "whitelist": []}

# 保存配置文件
def save_config(config):
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file)

# 清理临时文件夹
def clear_temp_folder(backup_folder, whitelist):
    temp_folder = tempfile.gettempdir()
    deleted_files = []
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        if file_path not in whitelist:
            shutil.move(file_path, backup_folder)
            deleted_files.append(file_path)
    return deleted_files

# 清理下载文件夹中的旧文件
def clear_download_folder(backup_folder, days=100, file_types=None, whitelist=[]):
    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    now = time.time()
    deleted_files = []
    for filename in os.listdir(download_folder):
        file_path = os.path.join(download_folder, filename)
        if file_path not in whitelist and (now - os.path.getmtime(file_path)) > days * 86400:
            if not file_types or file_path.endswith(tuple(file_types)):
                shutil.move(file_path, backup_folder)
                deleted_files.append(file_path)
    return deleted_files

# 自动清理任务
def auto_clean_task(config):
    while True:
        next_clean = datetime.now() + timedelta(days=config["clean_interval"])
        time.sleep((next_clean - datetime.now()).total_seconds())
        if datetime.now() >= next_clean:
            clear_temp_folder(config["backup_folder"], config["whitelist"])
            clear_download_folder(config["backup_folder"], days=100, whitelist=config["whitelist"])

# 生成清理报告
def generate_report(deleted_files, filename="cleanup_report.csv"):
    with open(filename, "w", newline="") as csvfile:
        report_writer = csv.writer(csvfile)
        report_writer.writerow(["File Path", "Deletion Time"])
        for file in deleted_files:
            report_writer.writerow([file, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    messagebox.showinfo("清理报告", f"清理报告已保存至 {filename}")

# 系统监控线程
def system_monitor():
    while True:
        time.sleep(5)  # 每5秒检查一次系统状况
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        if cpu_usage > 80 or memory_usage > 80 or disk_usage > 85:
            messagebox.showwarning("系统资源警告", f"CPU使用率: {cpu_usage}%, 内存使用率: {memory_usage}%, 磁盘使用率: {disk_usage}%")

# GUI 界面
class CleanupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能系统清理工具")
        self.config = read_config()
        self.backup_folder = self.config["backup_folder"]
        
        # GUI组件
        self.backup_label = Label(root, text="备份文件夹:")
        self.backup_label.pack()
        
        self.backup_entry = Entry(root, width=50)
        self.backup_entry.insert(0, self.backup_folder)
        self.backup_entry.pack()
        
        self.browse_button = Button(root, text="选择备份文件夹", command=self.browse_backup_folder)
        self.browse_button.pack()
        
        self.clean_temp_button = Button(root, text="清理临时文件夹", command=self.clean_temp_folder)
        self.clean_temp_button.pack()
        
        self.clean_download_button = Button(root, text="清理下载文件夹（按文件类型）", command=self.clean_download_folder)
        self.clean_download_button.pack()
        
        self.set_interval_button = Button(root, text="设置自动清理间隔", command=self.set_clean_interval)
        self.set_interval_button.pack()

        self.generate_report_button = Button(root, text="生成清理报告", command=self.generate_report)
        self.generate_report_button.pack()

        # 启动系统监控线程
        threading.Thread(target=system_monitor, daemon=True).start()
        if self.config.get("auto_clean", False):
            threading.Thread(target=auto_clean_task, args=(self.config,), daemon=True).start()

    def browse_backup_folder(self):
        folder_selected = filedialog.askdirectory()
