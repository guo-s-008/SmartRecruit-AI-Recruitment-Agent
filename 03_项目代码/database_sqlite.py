
"""
数据库操作模块 - SQLite版本
不需要MySQL服务器，开箱即用
"""
import sqlite3
import os
from config import SQLITE_DB_PATH

# 确保数据库目录存在
os.makedirs(os.path.dirname(SQLITE_DB_PATH) if os.path.dirname(SQLITE_DB_PATH) else ".", exist_ok=True)

def get_db_connection():
    """
    获取数据库连接
    :return: 数据库连接对象
    """
    return sqlite3.connect(SQLITE_DB_PATH)

def init_tables():
    """
    初始化所有表
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建岗位表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT UNIQUE NOT NULL,
            jd_content TEXT,
            scoring_criteria TEXT,
            education TEXT,
            city TEXT,
            is_intern INTEGER DEFAULT 0,
            hiring_count INTEGER DEFAULT 1,
            is_open INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建简历记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deliver_time TEXT,
            name TEXT,
            gender TEXT,
            age TEXT,
            education TEXT,
            major TEXT,
            city TEXT,
            target_city TEXT,
            job TEXT,
            score INTEGER,
            email TEXT,
            mail_status TEXT,
            result TEXT,
            interview_token TEXT,
            interview_link TEXT,
            interview_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建面试记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            email TEXT,
            candidate_name TEXT,
            resume_name TEXT,
            job_name TEXT,
            resume_id TEXT,
            status TEXT DEFAULT 'pending',
            questions_basic TEXT,
            questions_project TEXT,
            questions_intern TEXT,
            questions_practice TEXT,
            questions_advanced TEXT,
            answers TEXT,
            final_score REAL,
            scoring_details TEXT,
            result TEXT,
            interview_duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expired_at TIMESTAMP
        )
    ''')

    # 创建面试URL表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_url (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            token TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP,
            destroyed_at TIMESTAMP,
            request_count INTEGER DEFAULT 0,
            interrupted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resume_record(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库表初始化完成")

def save_interview_url(resume_id, url, token):
    """
    保存面试URL记录
    :param resume_id: 简历记录ID
    :param url: 面试URL
    :param token: 面试Token
    :return: 插入的ID
    """
    conn = None
    cursor = None
    inserted_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO interview_url (resume_id, url, token) VALUES (?, ?, ?)
        """
        cursor.execute(sql, (resume_id, url, token))
        inserted_id = cursor.lastrowid
        conn.commit()
        print(f"✅ 面试URL已保存，ID: {inserted_id}")
    except Exception as e:
        print(f"❌ 保存面试URL失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return inserted_id

def update_interview_url_request(token):
    """
    更新面试URL请求次数
    :param token: 面试Token
    :return: (是否中断, request_count)
    """
    conn = None
    cursor = None
    is_interrupted = False
    request_count = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询当前请求次数
        cursor.execute("SELECT request_count FROM interview_url WHERE token = ?", (token,))
        row = cursor.fetchone()

        if row:
            request_count = row[0] + 1
            cursor.execute("UPDATE interview_url SET request_count = ? WHERE token = ?", (request_count, token))

            # 如果是第一次使用，更新使用时间
            if request_count == 1:
                from datetime import datetime
                cursor.execute("UPDATE interview_url SET used_at = ? WHERE token = ?", (datetime.now().isoformat(), token))

            # 如果超过2次，标记为中断
            if request_count >= 3:
                is_interrupted = True
                from datetime import datetime
                cursor.execute("UPDATE interview_url SET interrupted = 1, destroyed_at = ? WHERE token = ?", (datetime.now().isoformat(), token))

            conn.commit()

    except Exception as e:
        print(f"❌ 更新面试URL失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return is_interrupted, request_count

def get_interview_url_by_token(token):
    """
    通过Token获取面试URL记录
    :param token: 面试Token
    :return: 记录字典
    """
    conn = None
    cursor = None
    record = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interview_url WHERE token = ?", (token,))
        row = cursor.fetchone()

        if row:
            cursor.execute("PRAGMA table_info(interview_url)")
            columns = [col[1] for col in cursor.fetchall()]
            record = dict(zip(columns, row))
    except Exception as e:
        print(f"❌ 查询面试URL失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return record

def mark_interview_url_destroyed(token):
    """
    标记面试URL为已销毁
    :param token: 面试Token
    """
    conn = None
    cursor = None
    try:
        from datetime import datetime
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE interview_url SET destroyed_at = ?, interrupted = 1 WHERE token = ?", (datetime.now().isoformat(), token))
        conn.commit()
        print(f"✅ 面试URL已销毁: {token}")
    except Exception as e:
        print(f"❌ 销毁面试URL失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_to_mysql(data):
    """
    保存简历记录到数据库
    :param data: 数据字典
    :return: 插入的ID，失败返回None
    """
    conn = None
    cursor = None
    inserted_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO resume_record 
        (deliver_time, job, major, education, city, target_city, score, email, mail_status, result) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            data["deliver_time"],
            data["job"],
            data["major"],
            data["education"],
            data["city"],
            data["target_city"],
            data["score"],
            data["email"],
            data["mail_status"],
            data["result"]
        ))

        inserted_id = cursor.lastrowid
        conn.commit()
        print("✅ 数据已存入数据库，ID:", inserted_id)
    except Exception as e:
        print("❌ 数据库错误：", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return inserted_id

def handle_save_to_db(detail_data):
    """
    封装的保存到数据库接口（供外部调用）
    :param detail_data: 详细数据字典
    :return: 插入的ID
    """
    data = {
        "deliver_time": detail_data.get("投递时间"),
        "job": detail_data.get("岗位"),
        "major": detail_data.get("专业"),
        "education": detail_data.get("学历"),
        "city": detail_data.get("所在城市"),
        "target_city": detail_data.get("意向地区"),
        "score": detail_data.get("得分"),
        "email": detail_data.get("邮箱"),
        "mail_status": detail_data.get("邮件状态"),
        "result": detail_data.get("测评结果")
    }
    return save_to_mysql(data)

def query_jobs_from_db(keyword=None):
    """
    从数据库查询岗位列表
    :param keyword: 关键词（可选）
    :return: 岗位名称列表
    """
    conn = get_db_connection()
    jobs = []
    try:
        cursor = conn.cursor()
        if keyword:
            sql = "SELECT job_name FROM job_positions WHERE is_open=1 AND job_name LIKE ?"
            cursor.execute(sql, (f"%{keyword}%",))
        else:
            sql = "SELECT job_name FROM job_positions WHERE is_open=1"
            cursor.execute(sql)
        jobs = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ 查询岗位失败: {e}")
    finally:
        conn.close()
    return jobs

def get_jd_from_db(job_name):
    """
    从数据库获取岗位JD
    :param job_name: 岗位名称
    :return: JD内容
    """
    conn = get_db_connection()
    jd_text = ""
    try:
        cursor = conn.cursor()
        sql = "SELECT jd_content FROM job_positions WHERE job_name LIKE ? AND is_open=1"
        cursor.execute(sql, (f"%{job_name}%",))
        row = cursor.fetchone()
        if row:
            jd_text = row[0]
    except Exception as e:
        print(f"❌ 查询JD失败: {e}")
    finally:
        conn.close()

    if not jd_text:
        jd_text = f"{job_name}：熟悉相关技术栈，有项目经验。"
    return jd_text

def get_scoring_criteria_from_db(job_name):
    """
    从数据库获取评分标准
    :param job_name: 岗位名称
    :return: 评分标准
    """
    conn = get_db_connection()
    criteria = ""
    try:
        cursor = conn.cursor()
        sql = "SELECT scoring_criteria FROM job_positions WHERE job_name LIKE ? AND is_open=1"
        cursor.execute(sql, (f"%{job_name}%",))
        row = cursor.fetchone()
        if row:
            criteria = row[0]
    except Exception as e:
        print(f"❌ 查询评分标准失败: {e}")
    finally:
        conn.close()
    return criteria

# 初始化数据库
init_tables()

