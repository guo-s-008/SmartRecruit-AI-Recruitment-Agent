"""
查看HR操作日志
"""
import os
from datetime import datetime

log_file = "/workspace/07_系统日志/log_hr/hr_" + datetime.now().strftime("%Y-%m-%d") + ".log"

print("=" * 80)
print("📋 HR操作日志查看")
print("=" * 80)

if os.path.exists(log_file):
    print(f"\n📂 日志文件: {log_file}\n")
    print("-" * 80)
    
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        if content:
            print(content)
        else:
            print("暂无日志记录")
    
    print("-" * 80)
else:
    print(f"\n❌ 日志文件不存在: {log_file}")
    print("\n📝 可用的日志文件：")
    
    log_dir = "/workspace/07_系统日志/log_hr/"
    if os.path.exists(log_dir):
        for filename in sorted(os.listdir(log_dir)):
            filepath = os.path.join(log_dir, filename)
            if os.path.isfile(filepath):
                print(f"  • {filename}")
    else:
        print("  暂无日志目录")

print("\n" + "=" * 80)
