
"""
初始化数据库数据
"""
import os
import sys

# 确保能找到项目模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import TARGET_JOBS
from database import get_db_connection
import json

def init_sample_jobs():
    """
    初始化示例岗位数据
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM job_positions WHERE is_open=1")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"数据库中已有 {count} 个岗位数据，跳过初始化。")
        conn.close()
        return

    print("正在初始化示例岗位数据...")

    # 示例岗位数据
    sample_jobs = [
        {
            "job_name": "AI大数据工程师",
            "jd_content": """【岗位名称】
AI大数据工程师

【岗位描述】
负责大数据平台的建设和维护，使用AI技术优化数据处理流程。

【任职要求】
1. 熟练掌握Python、Java或Scala等编程语言
2. 熟悉Hadoop、Spark等大数据技术栈
3. 有机器学习或深度学习相关经验者优先
4. 良好的团队协作和沟通能力""",
            "scoring_criteria": """专业匹配度: 30%
技能匹配度: 30%
项目经历匹配度: 25%
综合素养: 15%""",
            "education": "本科及以上",
            "city": "北京/杭州",
            "is_intern": 0,
            "hiring_count": 3
        },
        {
            "job_name": "大数据开发工程师",
            "jd_content": """【岗位名称】
大数据开发工程师

【岗位描述】
负责数据仓库建设、数据ETL开发、数据服务接口开发等工作。

【任职要求】
1. 熟练掌握Hive、Spark SQL等大数据工具
2. 熟悉数据仓库建模方法
3. 有实时数据处理经验者优先（Flink/Kafka）
4. 能独立完成复杂的SQL调优""",
            "scoring_criteria": """专业匹配度: 25%
技能匹配度: 35%
项目经历匹配度: 25%
综合素养: 15%""",
            "education": "本科及以上",
            "city": "深圳",
            "is_intern": 0,
            "hiring_count": 4
        },
        {
            "job_name": "数据分析师",
            "jd_content": """【岗位名称】
数据分析师

【岗位描述】
负责业务数据分析、数据报表开发、数据驱动决策支持等工作。

【任职要求】
1. 熟练掌握SQL和Excel高级功能
2. 熟悉Python/R数据分析工具
3. 有业务分析经验优先
4. 良好的数据敏感度和逻辑思维能力""",
            "scoring_criteria": """专业匹配度: 25%
技能匹配度: 30%
项目经历匹配度: 30%
综合素养: 15%""",
            "education": "本科及以上",
            "city": "广州",
            "is_intern": 1,
            "hiring_count": 2
        }
    ]

    # 插入数据
    for job in sample_jobs:
        try:
            cursor.execute('''
                INSERT INTO job_positions 
                (job_name, jd_content, scoring_criteria, education, city, is_intern, hiring_count, is_open)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                job['job_name'],
                job['jd_content'],
                job['scoring_criteria'],
                job['education'],
                job['city'],
                job['is_intern'],
                job['hiring_count']
            ))
            print(f"  ✓ 已添加岗位: {job['job_name']}")
        except Exception as e:
            print(f"  ✗ 添加岗位失败 {job['job_name']}: {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ 数据初始化完成！已添加 {len(sample_jobs)} 个岗位。")

if __name__ == "__main__":
    init_sample_jobs()
