
"""
数据库操作模块
负责所有 MySQL 数据库操作
"""
import pymysql
from pymysql import Error
from config import MYSQL_CONFIG


def get_db_connection():
    """
    获取数据库连接
    :return: 数据库连接对象
    """
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"]
    )


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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

        cursor.execute("SELECT LAST_INSERT_ID()")
        inserted_id = cursor.fetchone()[0]

        print("✅ 数据已存入 MySQL，ID:", inserted_id)
    except Error as e:
        print("❌ MySQL 错误：", e)
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
        with conn.cursor() as cur:
            if keyword:
                sql = "SELECT job_name FROM job_positions WHERE is_open=1 AND job_name LIKE %s"
                cur.execute(sql, (f"%{keyword}%",))
            else:
                sql = "SELECT job_name FROM job_positions WHERE is_open=1"
                cur.execute(sql)
            jobs = [row[0] for row in cur.fetchall()]
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
        with conn.cursor() as cur:
            sql = "SELECT jd_content FROM job_positions WHERE job_name LIKE %s AND is_open=1"
            cur.execute(sql, (f"%{job_name}%",))
            row = cur.fetchone()
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
        with conn.cursor() as cur:
            sql = "SELECT scoring_criteria FROM job_positions WHERE job_name LIKE %s AND is_open=1"
            cur.execute(sql, (f"%{job_name}%",))
            row = cur.fetchone()
            if row:
                criteria = row[0]
    except Exception as e:
        print(f"❌ 查询评分标准失败: {e}")
    finally:
        conn.close()
    return criteria

