import os
import shutil
import time
import logging
from threading import Thread
import send2trash  # 需要安装 pip install Send2Trash

# 日志文件路径
LOG_FILE = "cleanup_log.txt"
# 自定义垃圾文件类型和清理目录
CACHE_DIRS = [
    "/tmp", "/var/log", os.path.expanduser("~/.cache"), os.path.expanduser("~/Downloads")
]
JUNK_EXTENSIONS = [".tmp", ".log", ".bak", ".old", ".swp", ".DS_Store", "~", ".crdownload"]

# 配置日志
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def delete_file_safely(file_path):
    """将文件移至回收站"""
    try:
        send2trash.send2trash(file_path)
        logging.info(f"Safely deleted to trash: {file_path}")
        print(f"Moved to trash: {file_path}")
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {e}")
        print(f"Error deleting file {file_path}: {e}")

def clean_directory(directory, days_old=30, min_size=0):
    """
    清理目录中的垃圾文件并统计可释放空间

    Parameters:
    directory (str): 目标目录路径
    days_old (int): 删除文件的最小年龄（天）
    min_size (int): 文件最小大小（字节）
    """
    freed_space = 0
    now = time.time()
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if any(file_path.endswith(ext) for ext in JUNK_EXTENSIONS):
                file_age = now - os.path.getmtime(file_path)
                file_size = os.path.getsize(file_path)
                if file_age > days_old * 86400 and file_size >= min_size:
                    freed_space += file_size
                    delete_file_safely(file_path)
    return freed_space

def clean_cache():
    """清理指定的缓存目录并返回释放的总空间"""
    total_freed_space = 0
    threads = []
    for directory in CACHE_DIRS:
        if os.path.exists(directory):
            print(f"Cleaning {directory}...")
            thread = Thread(target=lambda: clean_directory(directory))
            threads.append(thread)
            thread.start()
    for thread in threads:
        thread.join()
    print(f"Total space freed: {total_freed_space / (1024 * 1024):.2f} MB")

def remove_empty_folders(path):
    """递归删除空文件夹"""
    for root, dirs, _ in os.walk(path, topdown=False):
        for dir_ in dirs:
            dir_path = os.path.join(root, dir_)
            try:
                os.rmdir(dir_path)
                logging.info(f"Deleted empty folder: {dir_path}")
                print(f"Deleted empty folder: {dir_path}")
            except OSError:
                pass

def display_statistics():
    """显示清理统计信息"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as log:
            lines = log.readlines()
        print("\n--- Cleanup Summary ---")
        print(f"Total items deleted: {len(lines)}")
    else:
        print("No cleanup log found.")

def estimate_cleanup_space(directory):
    """预估将释放的空间大小"""
    total_size = 0
    now = time.time()
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if any(file_path.endswith(ext) for ext in JUNK_EXTENSIONS):
                file_age = now - os.path.getmtime(file_path)
                if file_age > 30 * 86400:  # 默认清理30天以上的文件
                    total_size += os.path.getsize(file_path)
    print(f"Estimated cleanup space for {directory}: {total_size / (1024 * 1024):.2f} MB")

def main():
    # 估算清理前的可释放空间
    for directory in CACHE_DIRS:
        estimate_cleanup_space(directory)
    # 清理缓存并显示统计信息
    clean_cache()
    for directory in CACHE_DIRS:
        remove_empty_folders(directory)
    display_statistics()
    print("System cleanup complete.")

if __name__ == "__main__":
    user_choice = input("Select mode: (1) Regular Cleanup (2) View Cleanup Estimate\n")
    if user_choice == "1":
        main()
    elif user_choice == "2":
        for directory in CACHE_DIRS:
            estimate_cleanup_space(directory)
