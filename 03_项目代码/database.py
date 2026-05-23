
"""
数据库操作模块
自动切换SQLite和MySQL
"""
from config import USE_SQLITE

if USE_SQLITE:
    from database_sqlite import (
        get_db_connection,
        save_to_mysql,
        handle_save_to_db,
        query_jobs_from_db,
        get_jd_from_db,
        get_scoring_criteria_from_db,
        init_tables,
        save_interview_url,
        update_interview_url_request,
        get_interview_url_by_token,
        mark_interview_url_destroyed
    )
else:
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

    def init_tables():
        """
        初始化MySQL数据库表
        """
        # 先创建数据库（如果不存在）
        try:
            conn_temp = pymysql.connect(
                host=MYSQL_CONFIG["host"],
                port=MYSQL_CONFIG["port"],
                user=MYSQL_CONFIG["user"],
                password=MYSQL_CONFIG["password"],
                charset=MYSQL_CONFIG["charset"]
            )
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor_temp.close()
            conn_temp.close()
            print(f"✅ 数据库 {MYSQL_CONFIG['database']} 已创建或已存在")
        except Exception as e:
            print(f"❌ 创建数据库失败：{e}")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 创建岗位表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_positions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_name VARCHAR(200) UNIQUE NOT NULL COMMENT '岗位名称',
                jd_content TEXT COMMENT '岗位JD内容',
                scoring_criteria TEXT COMMENT '评分标准',
                education VARCHAR(100) COMMENT '学历要求',
                city VARCHAR(100) COMMENT '工作城市',
                is_intern TINYINT DEFAULT 0 COMMENT '是否实习岗',
                hiring_count INT DEFAULT 1 COMMENT '招聘人数',
                is_open TINYINT DEFAULT 1 COMMENT '是否开放',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位信息表'
        ''')

        # 2. 创建简历记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_record (
                id INT AUTO_INCREMENT PRIMARY KEY,
                deliver_time DATETIME COMMENT '投递时间',
                name VARCHAR(100) COMMENT '姓名',
                gender VARCHAR(20) COMMENT '性别',
                age VARCHAR(20) COMMENT '年龄',
                education VARCHAR(100) COMMENT '学历',
                major VARCHAR(200) COMMENT '专业',
                city VARCHAR(100) COMMENT '所在城市',
                target_city VARCHAR(200) COMMENT '意向城市',
                job VARCHAR(200) COMMENT '应聘岗位',
                score INT COMMENT '初筛得分',
                email VARCHAR(200) COMMENT '邮箱',
                mail_status VARCHAR(50) COMMENT '邮件状态',
                result VARCHAR(50) COMMENT '初筛结果',
                interview_token VARCHAR(200) COMMENT '面试Token',
                interview_link VARCHAR(500) COMMENT '面试链接',
                interview_status VARCHAR(50) DEFAULT 'pending' COMMENT '面试状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历投递记录表'
        ''')

        # 3. 创建面试记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_record (
                id INT AUTO_INCREMENT PRIMARY KEY,
                token VARCHAR(200) UNIQUE NOT NULL COMMENT '面试Token',
                email VARCHAR(200) COMMENT '面试者邮箱',
                candidate_name VARCHAR(100) COMMENT '面试者姓名',
                resume_name VARCHAR(200) COMMENT '简历文件名',
                job_name VARCHAR(200) COMMENT '应聘岗位',
                resume_id INT COMMENT '关联简历ID',
                status VARCHAR(50) DEFAULT 'pending' COMMENT '面试状态',
                questions_basic TEXT COMMENT '基础知识题目(JSON)',
                questions_project TEXT COMMENT '项目经历题目(JSON)',
                questions_intern TEXT COMMENT '实习经历题目(JSON)',
                questions_practice TEXT COMMENT '技能实战题目(JSON)',
                questions_advanced TEXT COMMENT '技能进阶题目(JSON)',
                answers TEXT COMMENT '所有回答(JSON)',
                final_score DECIMAL(5,2) COMMENT '最终得分',
                scoring_details TEXT COMMENT '评分详情(JSON)',
                result VARCHAR(50) COMMENT '面试结果',
                interview_duration INT COMMENT '面试用时(秒)',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                expired_at DATETIME COMMENT '链接过期时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI面试记录表'
        ''')

        # 4. 创建面试URL表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_url (
                id INT AUTO_INCREMENT PRIMARY KEY,
                resume_id INT NOT NULL COMMENT '关联简历记录ID',
                url VARCHAR(500) NOT NULL COMMENT '面试URL',
                token VARCHAR(200) NOT NULL COMMENT '面试Token',
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'URL生成时间',
                used_at TIMESTAMP NULL COMMENT '被使用时间',
                destroyed_at TIMESTAMP NULL COMMENT '销毁时间',
                request_count INT DEFAULT 0 COMMENT '请求次数',
                interrupted INT DEFAULT 0 COMMENT '是否中断：1=中断，0=正常',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (resume_id) REFERENCES resume_record(id) ON DELETE CASCADE,
                INDEX idx_token (token),
                INDEX idx_resume_id (resume_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='面试URL表'
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ MySQL数据库表初始化完成")

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
            INSERT INTO interview_url (resume_id, url, token) VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (resume_id, url, token))
            cursor.execute("SELECT LAST_INSERT_ID()")
            inserted_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ 面试URL已保存，ID: {inserted_id}")
        except Error as e:
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
            cursor.execute("SELECT request_count FROM interview_url WHERE token = %s", (token,))
            row = cursor.fetchone()

            if row:
                request_count = row[0] + 1
                cursor.execute("UPDATE interview_url SET request_count = %s WHERE token = %s", (request_count, token))

                # 如果是第一次使用，更新使用时间
                if request_count == 1:
                    from datetime import datetime
                    cursor.execute("UPDATE interview_url SET used_at = %s WHERE token = %s", (datetime.now(), token))

                # 如果超过2次，标记为中断
                if request_count >= 3:
                    is_interrupted = True
                    from datetime import datetime
                    cursor.execute("UPDATE interview_url SET interrupted = 1, destroyed_at = %s WHERE token = %s", (datetime.now(), token))

                conn.commit()

        except Error as e:
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
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM interview_url WHERE token = %s", (token,))
                record = cur.fetchone()
        except Error as e:
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
            cursor.execute("UPDATE interview_url SET destroyed_at = %s, interrupted = 1 WHERE token = %s", (datetime.now(), token))
            conn.commit()
            print(f"✅ 面试URL已销毁: {token}")
        except Error as e:
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get("deliver_time"),
                data.get("job"),
                data.get("major"),
                data.get("education"),
                data.get("city"),
                data.get("target_city"),
                data.get("score"),
                data.get("email"),
                data.get("mail_status"),
                data.get("result")
            ))

            cursor.execute("SELECT LAST_INSERT_ID()")
            inserted_id = cursor.fetchone()[0]
            conn.commit()

            print("✅ 数据已存入 MySQL，ID:", inserted_id)
        except Error as e:
            print("❌ MySQL 错误：", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return inserted_id

    def save_interview_to_db(interview_data):
        """
        保存面试记录到数据库
        :param interview_data: 面试数据字典
        :return: 插入的ID
        """
        import json
        conn = None
        cursor = None
        inserted_id = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
            INSERT INTO interview_record 
            (token, email, candidate_name, job_name, status, questions_basic, questions_project, 
             questions_intern, questions_practice, questions_advanced, final_score, result, 
             scoring_details, interview_duration)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                interview_data.get("token"),
                interview_data.get("email"),
                interview_data.get("candidate_name"),
                interview_data.get("job_name"),
                interview_data.get("status", "pending"),
                json.dumps(interview_data.get("questions_basic", []), ensure_ascii=False),
                json.dumps(interview_data.get("questions_project", []), ensure_ascii=False),
                json.dumps(interview_data.get("questions_intern", []), ensure_ascii=False),
                json.dumps(interview_data.get("questions_practice", []), ensure_ascii=False),
                json.dumps(interview_data.get("questions_advanced", []), ensure_ascii=False),
                interview_data.get("final_score"),
                interview_data.get("result"),
                json.dumps(interview_data.get("scoring_details", {}), ensure_ascii=False),
                interview_data.get("interview_duration")
            ))

            cursor.execute("SELECT LAST_INSERT_ID()")
            inserted_id = cursor.fetchone()[0]
            conn.commit()

            print("✅ 面试数据已存入 MySQL，ID:", inserted_id)
        except Error as e:
            print("❌ MySQL 错误：", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return inserted_id

    def update_interview_result(token, final_score, result, scoring_details):
        """
        更新面试结果
        :param token: 面试Token
        :param final_score: 最终得分
        :param result: 面试结果
        :param scoring_details: 评分详情
        """
        import json
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
            UPDATE interview_record 
            SET final_score=%s, result=%s, scoring_details=%s, status='completed'
            WHERE token=%s
            """
            cursor.execute(sql, (
                final_score,
                result,
                json.dumps(scoring_details, ensure_ascii=False),
                token
            ))
            conn.commit()
            print(f"✅ 面试结果已更新：{token}")
        except Error as e:
            print("❌ 更新面试结果失败：", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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

    def get_all_resumes():
        """
        获取所有简历记录
        :return: 简历记录列表
        """
        conn = get_db_connection()
        resumes = []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = "SELECT * FROM resume_record ORDER BY created_at DESC"
                cur.execute(sql)
                resumes = cur.fetchall()
        except Exception as e:
            print(f"❌ 查询简历记录失败: {e}")
        finally:
            conn.close()
        return resumes

    def get_all_interviews():
        """
        获取所有面试记录
        :return: 面试记录列表
        """
        conn = get_db_connection()
        interviews = []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = "SELECT * FROM interview_record ORDER BY created_at DESC"
                cur.execute(sql)
                interviews = cur.fetchall()
        except Exception as e:
            print(f"❌ 查询面试记录失败: {e}")
        finally:
            conn.close()
        return interviews

