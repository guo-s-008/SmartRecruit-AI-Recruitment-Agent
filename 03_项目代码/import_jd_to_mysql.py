# 文件名：import_jd_to_mysql.py
# 放到项目根目录，运行一次即可

import os
import pymysql
from dotenv import load_dotenv

# 加载 .env 中的数据库配置
load_dotenv("../04_数据文件/.env")

# 数据库连接
conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
    charset=os.getenv("MYSQL_CHARSET", "utf8mb4")
)

# JD 和评分标准文件夹
jd_dir = "../04_数据文件/job_jd"

# ==================== 手动预设每个岗位的固定信息 ====================
# 岗位名 → (学历要求, 任职城市, 是否有实习岗, 在招人数)
# 如果某个岗位不需要预设，可以留空，脚本会用默认值
JOB_CONFIG = {
    "AI大数据工程师":       ("本科及以上", "北京 / 杭州", 0, 3),
    "AI算法工程师":         ("硕士及以上", "上海", 0, 2),
    "AI应用开发工程师":     ("本科及以上", "杭州", 1, 5),
    "大数据开发工程师":     ("本科及以上", "深圳", 0, 4),
    "大数据运维开发工程师": ("本科及以上", "成都", 0, 3),
    "数据分析师":           ("本科及以上", "广州", 1, 2),
    "数据科学家":           ("硕士及以上", "北京", 0, 1),
    "推荐算法工程师":       ("本科及以上", "上海", 0, 2),
}

# ==================== 自动扫描并导入 ====================
# 收集所有岗位名（去掉 _jd.txt 和 _scoring.txt）
job_names = set()
for filename in os.listdir(jd_dir):
    if filename.endswith("_jd.txt"):
        job_name = filename.replace("_jd.txt", "")
        job_names.add(job_name)
    elif filename.endswith("_scoring.txt"):
        job_name = filename.replace("_scoring.txt", "")
        job_names.add(job_name)

for job_name in job_names:
    jd_file = os.path.join(jd_dir, f"{job_name}_jd.txt")
    scoring_file = os.path.join(jd_dir, f"{job_name}_scoring.txt")

    jd_content = ""
    scoring_content = ""

    # 读取 JD
    if os.path.exists(jd_file):
        with open(jd_file, "r", encoding="utf-8") as f:
            jd_content = f.read().strip()
        print(f"✅ 读取 JD：{job_name}")
    else:
        print(f"⚠️ 未找到 JD 文件：{jd_file}")

    # 读取评分标准
    if os.path.exists(scoring_file):
        with open(scoring_file, "r", encoding="utf-8") as f:
            scoring_content = f.read().strip()
        print(f"✅ 读取评分标准：{job_name}")
    else:
        print(f"⚠️ 未找到评分标准文件：{scoring_file}")

    if not jd_content and not scoring_content:
        continue

    # 取预设字段，没有则用默认
    edu, city, intern, count = JOB_CONFIG.get(job_name, ("本科及以上", "北京", 0, 1))

    with conn.cursor() as cursor:
        # 检查是否已存在该岗位
        cursor.execute("SELECT id FROM job_positions WHERE job_name=%s", (job_name,))
        if cursor.fetchone():
            # 更新已有
            cursor.execute(
                """UPDATE job_positions 
                   SET jd_content=%s, scoring_criteria=%s,
                       education=%s, city=%s, is_intern=%s, hiring_count=%s
                   WHERE job_name=%s""",
                (jd_content, scoring_content, edu, city, intern, count, job_name)
            )
            print(f"🔄 更新 {job_name}")
        else:
            # 插入新岗位
            cursor.execute(
                """INSERT INTO job_positions 
                   (job_name, jd_content, scoring_criteria, education, city, is_intern, hiring_count, is_open)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 1)""",
                (job_name, jd_content, scoring_content, edu, city, intern, count)
            )
            print(f"➕ 新增 {job_name}")

conn.commit()
conn.close()
print("🎉 所有 JD 和评分标准导入完成")