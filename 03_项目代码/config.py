
"""
配置管理模块
统一管理项目所有配置项
"""
import os
from dotenv import load_dotenv

# ===================== 加载环境变量 =====================
# 项目根目录（基于当前文件位置）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载 .env 文件
ENV_PATH = os.path.join(BASE_DIR, "04_数据文件", ".env")
load_dotenv(ENV_PATH)

# ===================== 路径配置 =====================
# 文件夹路径
UPLOAD_FOLDER = os.path.join(BASE_DIR, "01_简历投递收件箱")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "02_已处理简历")
JD_FOLDER = os.path.join(BASE_DIR, "04_数据文件", "job_jd")
LOG_ROOT = os.path.join(BASE_DIR, "07_系统日志")

# Excel 数据文件路径（优先使用环境变量，没有则使用默认相对路径）
EXCEL_DATA_PATH = os.getenv("EXCEL_DATA_PATH", os.path.join(BASE_DIR, "04_数据文件", "recruitment_data.xlsx"))

# ===================== 数据库配置 =====================
# 使用SQLite（默认，不需要服务器）
USE_SQLITE = True

# SQLite 数据库路径
SQLITE_DB_PATH = os.path.join(BASE_DIR, "04_数据文件", "recruitment.db")

# MySQL 数据库配置
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": os.getenv("MYSQL_CHARSET", "utf8mb4")
}

# ===================== 阿里云百炼 API 配置 =====================
API_CONFIG = {
    "key": os.getenv("API_KEY"),
    "url": os.getenv("API_URL"),
    "model": os.getenv("API_MODEL", "qwen-turbo")
}

# ===================== 邮件配置 =====================
EMAIL_CONFIG = {
    "sender": os.getenv("MAIL_SENDER"),
    "password": os.getenv("MAIL_PASSWORD"),
    "server": os.getenv("MAIL_SERVER", "smtp.qq.com"),
    "port": int(os.getenv("MAIL_PORT", 465)),
    "hr_email": os.getenv("HR_EMAIL")
}

# ===================== 应用配置 =====================
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

# ===================== 面试配置 =====================
INTERVIEW_CONFIG = {
    "token_expire_hours": 48,
    "module_names": ["基础知识", "项目经历", "实习经历", "技能实战", "技能进阶实战"],
    "module_weights": [0.1, 0.3, 0.3, 0.2, 0.1],
    "questions_per_module": [2, 3, 3, 2, 2]
}

# ===================== 岗位列表（用于页面展示） =====================
TARGET_JOBS = [
    "AI大数据工程师",
    "AI算法工程师",
    "AI应用开发工程师",
    "大数据开发工程师",
    "大数据运维开发工程师",
    "数据分析师",
    "数据科学家",
    "推荐算法工程师"
]

# ===================== 自动创建必要目录 =====================
for folder_path in [UPLOAD_FOLDER, PROCESSED_FOLDER, JD_FOLDER, LOG_ROOT]:
    os.makedirs(folder_path, exist_ok=True)

