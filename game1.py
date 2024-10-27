import os
import shutil
import tempfile
import psutil
import time
import json
import threading
import schedule
import smtplib
import csv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox, filedialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置文件和默认设置
CONFIG_FILE = "cleanup_config.json"
DEFAULT_BACKUP_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "Backup")
AUTO_CLEAN_INTERVAL = 7  # 默认每7天自动清理一次
LOG_FILE = "cleanup_log.csv"  # 日志文件，用于记录清理历史

# 读取和保存配置文件
def read_config():
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        return {"backup_folder": DEFAULT_BACKUP_FOLDER, "clean_interval": AUTO_CLEAN_INTERVAL, "whitelist": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file)

# 保存日志
def log_cleanup(action, files_deleted):
    with open(LOG_FILE, "a", newline='') as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow([datetime.now(), action, len(files_deleted), files_deleted])

# 清理模块
def clear_temp_folder(backup_folder, whitelist):
    temp_folder = tempfile.gettempdir()
    deleted_files = []
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        if os.path.isfile(file_path) and file_path not in whitelist:
            shutil.move(file_path, backup_folder)
            deleted_files.append(file_path)
    log_cleanup("Temporary Files Cleanup", deleted_files)
    return deleted_files

def clear_download_folder(backup_folder, whitelist, days=100):
    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    now = time.time()
    deleted_files = []
    for filename in os.listdir(download_folder):
        file_path = os.path.join(download_folder, filename)
        if os.path.isfile(file_path) and file_path not in whitelist and (now - os.path.getmtime(file_path)) > days * 86400:
            shutil.move(file_path, backup_folder)
            deleted_files.append(file_path)
    log_cleanup("Download Folder Cleanup", deleted_files)
    return deleted_files

# 清理操作函数
def run_cleanup():
    config = read_config()
    backup_folder = config.get("backup_folder", DEFAULT_BACKUP_FOLDER)
    whitelist = config.get("whitelist", [])

    deleted_temp_files = clear_temp_folder(backup_folder, whitelist)
    deleted_download_files = clear_download_folder(backup_folder, whitelist)
    messagebox.showinfo("清理完成", f"已清理 {len(deleted_temp_files)} 个临时文件，{len(deleted_download_files)} 个下载文件。")

# 邮件通知模块
def send_email_report(subject, body, recipient_email):
    config = read_config()
    sender_email = config.get("email")
    sender_password = config.get("email_password")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

# 自动清理设置
def setup_auto_cleanup():
    config = read_config()
    interval = config.get("clean_interval", AUTO_CLEAN_INTERVAL)
    schedule.every(interval).days.do(run_cleanup)

    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(3600)

    threading.Thread(target=scheduler_loop, daemon=True).start()

# 主程序入口
if __name__ == "__main__":
    config = read_config()
    root = Tk()
    root.title("智能系统清理工具")

    # 备份文件夹配置
    Label(root, text="备份文件夹:").pack()
    backup_entry = Entry(root, width=50)
    backup_entry.insert(0, config.get("backup_folder", DEFAULT_BACKUP_FOLDER))
    backup_entry.pack()

    def save_settings():
        config['backup_folder'] = backup_entry.get()
        config['clean_interval'] = int(interval_entry.get())
        save_config(config)
        messagebox.showinfo("设置已保存", "备份文件夹和清理间隔设置已保存。")

    Button(root, text="保存设置", command=save_settings).pack()

    # 清理间隔配置
    Label(root, text="清理间隔（天）:").pack()
    interval_entry = Entry(root, width=5)
    interval_entry.insert(0, str(config.get("clean_interval", AUTO_CLEAN_INTERVAL)))
    interval_entry.pack()

    # 手动清理按钮
    def start_manual_cleanup():
        response = messagebox.askyesno("确认清理", "是否开始清理？")
        if response:
            run_cleanup()

    Button(root, text="开始清理", command=start_manual_cleanup).pack()

    # 启动自动清理和监控
    setup_auto_cleanup()
    root.mainloop()
