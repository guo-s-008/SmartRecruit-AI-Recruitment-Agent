
"""
岗位数据导入脚本
将job_jd目录下的JD和评分标准导入到数据库
"""
import os
import sqlite3
from config import SQLITE_DB_PATH


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(SQLITE_DB_PATH)


def read_file(file_path):
    """读取文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_job_name(filename):
    """从文件名解析岗位名称"""
    # 移除后缀
    if filename.endswith('_jd.txt'):
        return filename.replace('_jd.txt', '')
    elif filename.endswith('_scoring.txt'):
        return filename.replace('_scoring.txt', '')
    return None


def import_jobs():
    """导入所有岗位数据"""
    job_jd_dir = '/workspace/04_数据文件/job_jd'
    
    if not os.path.exists(job_jd_dir):
        print(f"❌ 目录不存在: {job_jd_dir}")
        return
    
    # 获取所有文件
    files = os.listdir(job_jd_dir)
    
    # 按岗位分组
    job_data = {}
    
    for filename in files:
        if filename.endswith('_jd.txt') or filename.endswith('_scoring.txt'):
            job_name = parse_job_name(filename)
            if job_name:
                if job_name not in job_data:
                    job_data[job_name] = {'jd': None, 'scoring': None}
                
                file_path = os.path.join(job_jd_dir, filename)
                content = read_file(file_path)
                
                if filename.endswith('_jd.txt'):
                    job_data[job_name]['jd'] = content
                else:
                    job_data[job_name]['scoring'] = content
    
    if not job_data:
        print("❌ 未找到岗位数据文件")
        return
    
    # 连接数据库
    conn = get_db_connection()
    cursor = conn.cursor()
    
    success_count = 0
    
    for job_name, data in job_data.items():
        try:
            # 检查是否已存在
            cursor.execute("SELECT id FROM job_positions WHERE job_name = ?", (job_name,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新
                cursor.execute("""
                    UPDATE job_positions 
                    SET jd_content = ?, scoring_criteria = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE job_name = ?
                """, (data['jd'], data['scoring'], job_name))
                print(f"✅ 更新岗位: {job_name}")
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO job_positions 
                    (job_name, jd_content, scoring_criteria, is_open)
                    VALUES (?, ?, ?, 1)
                """, (job_name, data['jd'], data['scoring']))
                print(f"✅ 新增岗位: {job_name}")
            
            success_count += 1
        except Exception as e:
            print(f"❌ 处理岗位 {job_name} 失败: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 导入完成！成功处理 {success_count} 个岗位")


if __name__ == "__main__":
    import_jobs()

