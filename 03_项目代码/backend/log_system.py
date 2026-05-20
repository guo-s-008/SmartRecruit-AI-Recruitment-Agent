import os
import time
from datetime import datetime

# 根日志目录（绝对路径）
LOG_ROOT = r"../07_系统日志"

# 子日志目录
LOG_EMAIL = os.path.join(LOG_ROOT, "log_eminfo")   # 邮件&详情日志
LOG_DAY = os.path.join(LOG_ROOT, "log_dayinfo")     # 每日投递统计日志

# 自动创建文件夹
os.makedirs(LOG_EMAIL, exist_ok=True)
os.makedirs(LOG_DAY, exist_ok=True)


# ===================== 1. 获取今日日志文件 =====================
def get_today_log_file(folder):
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(folder, f"{today}.log")


# ===================== 2. 写入【详情日志】（邮件+简历+得分+状态） =====================
def write_email_detail_log(content):
    log_path = get_today_log_file(LOG_EMAIL)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(content + "\n" + "="*80 + "\n")


# ===================== 3. 写入【每日投递日志】（你原来的日志格式） =====================
def write_recruit_log(resume_name, job_name, score, email, mail_status, result_status, remark=""):
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = (
        f"【{now_time}】简历：{resume_name}，岗位：{job_name}，得分：{score}，"
        f"求职者邮箱：{email}，邮件状态：{mail_status}，测评结果：{result_status}，备注：{remark}"
    )

    log_path = get_today_log_file(LOG_DAY)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)  # 再次确保目录存在
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_text + "\n")
        print(f"✅ 投递日志已写入：{log_path}")
    except Exception as e:
        print(f"❌ 投递日志写入失败：{e}")

# ===================== 对话日志目录与函数 =====================
LOG_DIALOG = os.path.join(LOG_ROOT, "log_dialog")
os.makedirs(LOG_DIALOG, exist_ok=True)

def get_dialog_log_file():
    """返回今日对话日志文件路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIALOG, f"dialog_{today}.log")

def write_dialog_log(role, content):
    """
    记录单条对话消息
    role: "user" / "assistant" / "system"
    content: 消息文本
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{role.upper()}] {content}\n"
    log_path = get_dialog_log_file()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"对话日志写入失败: {e}")