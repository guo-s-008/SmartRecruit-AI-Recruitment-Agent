
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

    # 创建人才库表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talent_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            age TEXT,
            education TEXT,
            major TEXT,
            city TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            skills TEXT,
            experience TEXT,
            resume_text TEXT,
            tags TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# ==================== 人才库操作函数 ====================

def add_talent_to_pool(talent_data):
    """
    添加人才到人才库
    :param talent_data: 人才数据字典
    :return: 插入的ID
    """
    conn = None
    cursor = None
    inserted_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT OR REPLACE INTO talent_pool 
        (name, gender, age, education, major, city, email, phone, skills, experience, resume_text, tags, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            talent_data.get("name"),
            talent_data.get("gender"),
            talent_data.get("age"),
            talent_data.get("education"),
            talent_data.get("major"),
            talent_data.get("city"),
            talent_data.get("email"),
            talent_data.get("phone"),
            talent_data.get("skills"),
            talent_data.get("experience"),
            talent_data.get("resume_text"),
            talent_data.get("tags"),
            talent_data.get("source", "简历投递")
        ))
        inserted_id = cursor.lastrowid
        conn.commit()
        print(f"✅ 人才已添加到人才库，ID: {inserted_id}")
    except Exception as e:
        print(f"❌ 添加人才失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return inserted_id

def get_all_talents(status=None):
    """
    获取所有人才
    :param status: 状态筛选（可选）
    :return: 人才列表
    """
    conn = get_db_connection()
    talents = []
    try:
        cursor = conn.cursor()
        if status:
            sql = "SELECT * FROM talent_pool WHERE status=? ORDER BY last_updated DESC"
            cursor.execute(sql, (status,))
        else:
            sql = "SELECT * FROM talent_pool ORDER BY last_updated DESC"
            cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(talent_pool)")
        columns = [col[1] for col in cursor.fetchall()]
        talents = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ 查询人才库失败: {e}")
    finally:
        conn.close()
    return talents

def search_talents(keyword=None, education=None, city=None, skills=None):
    """
    搜索人才
    :param keyword: 关键词
    :param education: 学历
    :param city: 城市
    :param skills: 技能
    :return: 人才列表
    """
    conn = get_db_connection()
    talents = []
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM talent_pool WHERE status='active' "
        params = []
        
        if keyword:
            sql += "AND (name LIKE ? OR skills LIKE ? OR experience LIKE ?) "
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        if education:
            sql += "AND education=? "
            params.append(education)
        
        if city:
            sql += "AND city=? "
            params.append(city)
        
        if skills:
            sql += "AND skills LIKE ? "
            params.append(f"%{skills}%")
        
        sql += "ORDER BY last_updated DESC"
        cursor.execute(sql, params)
        
        rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(talent_pool)")
        columns = [col[1] for col in cursor.fetchall()]
        talents = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ 搜索人才失败: {e}")
    finally:
        conn.close()
    return talents

def recommend_talents_for_job(job_name, limit=5):
    """
    为岗位推荐人才（基于技能匹配）
    :param job_name: 岗位名称
    :param limit: 返回数量
    :return: 推荐人才列表
    """
    conn = get_db_connection()
    talents = []
    try:
        cursor = conn.cursor()
        
        # 获取岗位JD中的技能关键词
        cursor.execute("SELECT jd_content FROM job_positions WHERE job_name=?", (job_name,))
        row = cursor.fetchone()
        jd_content = row[0] if row else ""
        
        # 提取技能关键词（简单匹配）
        skill_keywords = ["python", "java", "go", "sql", "大数据", "机器学习", "数据分析", "算法"]
        
        # 搜索匹配的人才
        sql = "SELECT * FROM talent_pool WHERE status='active' AND ("
        conditions = []
        params = []
        for keyword in skill_keywords:
            conditions.append("skills LIKE ?")
            params.append(f"%{keyword}%")
        sql += " OR ".join(conditions)
        sql += ") ORDER BY last_updated DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(talent_pool)")
        columns = [col[1] for col in cursor.fetchall()]
        talents = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ 推荐人才失败: {e}")
    finally:
        conn.close()
    return talents

def update_talent_status(talent_id, status):
    """
    更新人才状态
    :param talent_id: 人才ID
    :param status: 新状态
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE talent_pool SET status=?, last_updated=? WHERE id=?",
                      (status, datetime.now().isoformat(), talent_id))
        conn.commit()
        print(f"✅ 人才状态已更新，ID: {talent_id}")
    except Exception as e:
        print(f"❌ 更新人才状态失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_job_to_db(job_data):
    """
    添加岗位到数据库
    :param job_data: 岗位数据字典
    :return: 插入的ID
    """
    conn = None
    cursor = None
    inserted_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO job_positions 
        (job_name, jd_content, scoring_criteria, education, city, is_intern, hiring_count, is_open)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_name) DO UPDATE SET
        jd_content=excluded.jd_content,
        scoring_criteria=excluded.scoring_criteria,
        education=excluded.education,
        city=excluded.city,
        is_intern=excluded.is_intern,
        hiring_count=excluded.hiring_count,
        is_open=excluded.is_open,
        updated_at=CURRENT_TIMESTAMP
        """
        cursor.execute(sql, (
            job_data.get("job_name"),
            job_data.get("jd_content"),
            job_data.get("scoring_criteria"),
            job_data.get("education"),
            job_data.get("city"),
            job_data.get("is_intern", 0),
            job_data.get("hiring_count", 1),
            job_data.get("is_open", 1)
        ))
        
        cursor.execute("SELECT id FROM job_positions WHERE job_name=?", (job_data.get("job_name"),))
        result = cursor.fetchone()
        inserted_id = result[0] if result else None
        
        conn.commit()
        print(f"✅ 岗位已添加到数据库，ID: {inserted_id}")
    except Exception as e:
        print(f"❌ 添加岗位失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return inserted_id

def get_all_jobs():
    """
    获取所有岗位
    :return: 岗位列表
    """
    conn = get_db_connection()
    jobs = []
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM job_positions ORDER BY created_at DESC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(job_positions)")
        columns = [col[1] for col in cursor.fetchall()]
        jobs = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ 查询岗位失败: {e}")
    finally:
        conn.close()
    return jobs

def update_job_status(job_id, is_open):
    """
    更新岗位状态
    :param job_id: 岗位ID
    :param is_open: 是否开放
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE job_positions SET is_open=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                      (is_open, job_id))
        conn.commit()
        print(f"✅ 岗位状态已更新，ID: {job_id}")
    except Exception as e:
        print(f"❌ 更新岗位状态失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_job(job_id):
    """
    删除岗位
    :param job_id: 岗位ID
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_positions WHERE id=?", (job_id,))
        conn.commit()
        print(f"✅ 岗位已删除，ID: {job_id}")
    except Exception as e:
        print(f"❌ 删除岗位失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_all_resumes():
    """
    获取所有简历记录
    :return: 简历列表
    """
    conn = get_db_connection()
    resumes = []
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM resume_record ORDER BY created_at DESC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(resume_record)")
        columns = [col[1] for col in cursor.fetchall()]
        resumes = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ 查询简历失败: {e}")
    finally:
        conn.close()
    return resumes

def get_all_interviews():
    """
    获取所有面试记录
    :return: 面试列表
    """
    conn = get_db_connection()
    interviews = []
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM interview_record ORDER BY created_at DESC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(interview_record)")
        columns = [col[1] for col in cursor.fetchall()]
        interviews = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ 查询面试记录失败: {e}")
    finally:
        conn.close()
    return interviews

# 初始化数据库
init_tables()

