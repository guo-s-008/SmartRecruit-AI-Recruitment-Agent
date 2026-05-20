
"""
验证岗位数据导入结果
"""
import sqlite3
from config import SQLITE_DB_PATH


def get_db_connection():
    return sqlite3.connect(SQLITE_DB_PATH)


def verify_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=== 数据库中的岗位列表 ===\n")
    
    cursor.execute("SELECT id, job_name, is_open, created_at FROM job_positions ORDER BY id")
    jobs = cursor.fetchall()
    
    for job in jobs:
        job_id, job_name, is_open, created_at = job
        status = "✅ 开放" if is_open else "❌ 关闭"
        print(f"ID: {job_id} | {status} | {job_name}")
        print(f"    创建时间: {created_at}")
        
        # 查看JD和评分标准的长度
        cursor.execute("SELECT LENGTH(jd_content), LENGTH(scoring_criteria) FROM job_positions WHERE id = ?", (job_id,))
        jd_len, scoring_len = cursor.fetchone()
        print(f"    JD长度: {jd_len} 字符 | 评分标准长度: {scoring_len} 字符")
        print()
    
    conn.close()
    
    print(f"\n总计: {len(jobs)} 个岗位")


if __name__ == "__main__":
    verify_jobs()

