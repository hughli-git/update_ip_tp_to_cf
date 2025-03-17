import os
import psutil
import sys


def check_duplicate_script():
    current_process = psutil.Process()
    current_script_path = sys.argv[0]
    current_script_name = os.path.basename(current_script_path)  # 获取当前脚本的文件名
    print(f"current_script_name {current_script_name}")

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # 检查是否是 Python 进程
            if "python" in proc.info["name"].lower():
                # 获取进程的命令行参数
                cmdline = proc.info["cmdline"]
                if cmdline:
                    # 检查命令行参数中是否包含当前脚本的路径
                    if current_script_name in " ".join(cmdline):
                        # 排除当前进程
                        if proc.pid != current_process.pid:
                            print(f"Duplicate script detected: {cmdline} {proc.pid}")
                            sys.exit(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
