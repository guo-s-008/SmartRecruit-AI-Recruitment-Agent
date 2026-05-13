"""
agent_service.py - 后端服务层
封装数据库查询 + 大模型API调用 + 复用 agent.py 中的邮件/日志/存储函数
所有供前端 chat_main.py 调用的函数都在这里
"""
import os
import re
import json
import requests
import pymysql
from dotenv import load_dotenv
import hashlib
import secrets
from datetime import datetime, timedelta
import pandas as pd
# ==================== 加载环境变量 ====================
# .env 文件位于 ../04_数据文件/ 目录，包含 API_KEY、数据库配置等
load_dotenv("../04_数据文件/.env")

API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")

# ==================== 导入原有 agent.py 中的底层函数 ====================
# 这些函数保持不变，我们只是在这里重新封装一层
from agent import (
    read_resume_text as _read_resume_text,  # 从文件读取简历文本（支持pdf/docx/txt）
    extract_email as _extract_email,        # 从文本中提取邮箱地址
    send_email as _send_email,              # 实际发送邮件的函数（SMTP）
    save_to_mysql as _save_to_mysql,        # 将简历评分结果写入MySQL
    write_recruit_log as _write_recruit_log # 写入招聘业务日志（log_dayinfo）
)


# ==================== MySQL 连接工具 ====================
def get_db_connection():
    """返回一个MySQL数据库连接，配置从环境变量读取"""
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE, charset=MYSQL_CHARSET
    )


# ==================== 1. 从数据库查询在招岗位 ====================
def query_jobs_from_db(keyword=None):
    """
    从 job_positions 表中查询所有开放中的岗位名称
    如果提供 keyword，则按关键词模糊匹配
    返回：岗位名称列表，如 ["数据分析师", "AI应用开发工程师"]
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


# ==================== 2. 从数据库读取岗位JD ====================
def get_jd_from_db(job_name):
    """
    根据岗位名模糊查询 job_positions 表中的 jd_content 字段
    注意：使用 LIKE 匹配，因此传入 "AI开发" 也能匹配到 "AI应用开发工程师"
    如果查询不到，返回一个默认的提示文本
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

    # 兜底：如果没查到，返回一个友善提示
    if not jd_text:
        jd_text = f"{job_name}：熟悉相关技术栈，有项目经验。"
    return jd_text


# ==================== 3. 调用大模型API（通用函数） ====================
def call_llm(messages, temperature=0.3):
    """
    向阿里云百炼大模型发送请求并返回回复内容
    messages: 标准 Chat 格式列表，如 [{"role":"user","content":"..."}]
    temperature: 控制输出的随机性，0 为确定，1 为多样
    返回：大模型生成的文本内容，失败时返回错误信息
    """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "qwen-turbo",  # 可根据需要更换为 qwen-plus / qwen-max
        "messages": messages,
        "temperature": temperature
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API返回异常：{data}"
    except Exception as e:
        return f"AI调用失败：{str(e)}"


# ==================== 新增：文本摘要精简函数 ====================
def summarize_text(text, max_length=100):
    """
    将一段较长的评估意见精简为核心摘要（用于HR邮件）
    如果原文已经足够短，直接返回原文；否则调用大模型进行摘要
    若大模型调用失败，则直接截取前 max_length 个字符作为回退
    """
    if not text or len(text) <= max_length:
        return text

    prompt = f"""
请将以下招聘评估意见精简为不超过{max_length}字的摘要，只保留最核心的优点或不足，去掉客套话、重复描述和模糊表达。

原文：
{text}

精简结果："""
    try:
        summary = call_llm([{"role": "user", "content": prompt}], temperature=0.2)
        return summary.strip()[:max_length]
    except:
        # 摘要失败时，采用暴力截断
        return text[:max_length] + "..."


# ==================== 4. 解析上传的简历 ====================
def handle_upload_and_parse(file_bytes, filename):
    temp_dir = "../01_简历投递收件箱"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"_parse_{filename}")
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    text = _read_resume_text(temp_path)
    email = _extract_email(text)

    # ===== 原有正则提取 =====
    name = ""
    # 先尝试匹配"姓名：xxx"
    m = re.search(r'(姓名|名字)[：:]\s*([^\n\t\r]{2,4})', text)
    if m:
        name = m.group(2).strip()
    # 如果没匹配到，尝试取第一行中文
    if not name:
        first_line = text.strip().split("\n")[0].strip()
        if re.match(r'^[\u4e00-\u9fa5]{2,4}$', first_line):
            name = first_line

    gender = ""
    m = re.search(r'(性别)[：:]?\s*(男|女)', text)
    if m:
        gender = m.group(2)
    if not gender:
        if '男' in text[:300]:
            gender = '男'
        elif '女' in text[:300]:
            gender = '女'

    age = ""
    m = re.search(r'(出生年月|出生日期|生日)[：:]\s*(\d{4})', text)
    if m:
        try:
            age = str(2026 - int(m.group(2)[:4]))
        except:
            pass
    if not age:
        m = re.search(r'年龄[：:]\s*(\d{2})', text)
        if m:
            age = m.group(1)

    major = ""
    m = re.search(r"专业[:：]\s*([^\n\t\r]{2,20})", text)
    if m:
        major = m.group(1).strip()

    education = ""
    for edu in ["博士", "硕士", "研究生", "本科", "大专"]:
        if edu in text:
            education = edu
            break

    city = ""
    m = re.search(r"(所在城市|现居|城市|地址)[：:]\s*([^\n\t\r]{2,10})", text)
    if m:
        city = m.group(2).strip()

    # ===== 兜底：正则没提取到的，用大模型补 =====
    if not name or not gender or not age:
        try:
            prompt = f"""从以下简历文本中提取姓名、性别、年龄。
如果文本中没有相关信息，返回空字符串。
只返回JSON：{{"name":"...","gender":"...","age":"..."}}

简历文本：
{text[:800]}"""
            content = call_llm([{"role":"user","content":prompt}], temperature=0.0)
            info = json.loads(content)
            name = name or info.get("name", "")
            gender = gender or info.get("gender", "")
            age = age or info.get("age", "")
        except:
            pass  # 大模型失败就算了，保持原值

    try:
        os.remove(temp_path)
    except:
        pass

    return {
        "text": text,
        "email": email,
        "name": name,
        "gender": gender,
        "age": age,
        "major": major,
        "education": education,
        "city": city,
        "target_city": ""
    }
# ==================== 新增：从数据库读取评分标准 ====================
def get_scoring_criteria_from_db(job_name):
    """
    从 job_positions 表中读取该岗位的 AI 评分标准（scoring_criteria 字段）
    如果该岗位没有配置评分标准，返回空字符串，后续 Prompt 会使用默认维度
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


# ==================== 5. AI评分（返回结构化JSON） ====================
def handle_score(job_name, resume_text, jd_content):
    """
    调用大模型对简历进行评分，返回一个字典，包含：
    - score: 总分（整数）
    - report: 完整的结构化评分报告（求职者邮件用）
    - advantage: 简历优点（简短，网页展示用）
    - shortcoming: 简历不足与改进建议（简短，网页展示用）
    """
    scoring_criteria = get_scoring_criteria_from_db(job_name)

    prompt = f"""你是专业HR面试官，请根据【岗位JD】和【评分标准】对候选人简历进行严格评分（满分100）。

【岗位名称】{job_name}
【岗位JD要求】{jd_content}
【评分标准】{scoring_criteria if scoring_criteria else "请按专业匹配度、技能匹配度、项目经验匹配度、学历/经验匹配度四个维度自主评分，满分100。"}

【简历内容】{resume_text[:3000]}

请严格按照以下格式输出完整的评分报告（这个报告将直接作为邮件正文发送给求职者，请务必详细、专业）：

【简历评分】
分数：xx

【分项评分标准】
1. 专业匹配度：xx分
2. 技能匹配度：xx分
3. 项目经验匹配度：xx分
4. 综合素养：xx分

【简历优势】
- 具体列出与JD匹配的亮点，每条用“- ”开头，至少写3条，要结合简历中的具体内容
- 每条优势都要有具体的技能/项目/经验支撑

【简历不足与改进建议】
- 具体列出与JD要求有明显差距的地方，每条用“- ”开头，至少写3条
- 针对每条不足给出可操作的改进建议

在报告最后，额外返回一个 JSON 片段（仅此片段，不要混入正文）：
{{"short_advantage": "简历优点摘要（50字以内，用于网页快速展示）", "short_shortcoming": "简历不足摘要（50字以内，用于网页快速展示）"}}
"""
    content = call_llm([{"role": "user", "content": prompt}], temperature=0.1)

    # 提取 JSON 片段
    short_advantage = ""
    short_shortcoming = ""
    full_report = content

    # 尝试从回复中提取 JSON（在最后一行或倒数第二行）
    lines = content.strip().split("\n")
    json_str = None
    for line in reversed(lines):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            json_str = line
            break
    if not json_str:
        # 兼容 { ... } 跨行的情况
        try:
            start = content.rfind("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = content[start:end+1]
        except:
            pass

    if json_str:
        try:
            short_data = json.loads(json_str)
            short_advantage = short_data.get("short_advantage", "")
            short_shortcoming = short_data.get("short_shortcoming", "")
            # 从报告中移除 JSON 部分，保持报告干净
            full_report = content.replace(json_str, "").strip()
        except:
            pass

    # 提取分数
    score = 0
    match = re.findall(r"分数[：:]\s*(\d+)", full_report)
    if match:
        score = int(match[0])

    # 如果 JSON 提取失败，回退为从报告中截取
    if not short_advantage:
        if "【简历优势】" in full_report:
            parts = full_report.split("【简历优势】")[-1].split("【简历不足与改进建议】")
            short_advantage = parts[0].strip()[:100] if parts else ""
    if not short_shortcoming:
        if "【简历不足与改进建议】" in full_report:
            parts = full_report.split("【简历不足与改进建议】")[-1].split("——————————————")[0]
            short_shortcoming = parts.strip()[:100]

    if not short_advantage:
        short_advantage = "简历与岗位要求基本匹配"
    if not short_shortcoming:
        short_shortcoming = "建议补充项目量化成果与核心技能"

    return {
        "score": score,
        "report": full_report,           # 完整报告，给求职者邮件用
        "advantage": short_advantage,     # 简短优点，网页展示用
        "shortcoming": short_shortcoming # 简短不足，网页展示用
    }

# ==================== 6. 智能追问（根据简历内容回答用户问题） ====================
def ask_resume_question(resume_text, question):
    """
    用户完成评分后，可以针对简历提出具体问题（如"我的不足是什么？"），
    本函数将简历内容和用户问题一起发送给大模型，生成有针对性的回答
    """
    prompt = f"""你是一位专业招聘顾问，根据候选人简历内容回答其问题。

【简历内容】
{resume_text[:2000]}

【候选人问题】
{question}

请给出具体、有针对性、可操作的回答。如果简历中缺乏相关信息，也请诚实指出。"""
    return call_llm([{"role": "user", "content": prompt}], temperature=0.5)


# ==================== 7. 发送邮件（含摘要精简） ====================
def handle_send_email(receive_email, score, job_title, apply_result, report="", advantage="", shortcoming=""):
    """
    发送邮件前对优势/不足进行二次精简（调用 summarize_text），
    确保 HR 收到的邮件只包含核心信息，求职者收到的报告保持完整。
    参数 apply_result 已经在前端计算好（"录用" 或 "不合适"），避免在邮件函数内做分数比较。
    """
    # 对长处和短板进行摘要，每个最多 100 字
    short_adv = summarize_text(advantage, 100) if advantage else ""
    short_short = summarize_text(shortcoming, 100) if shortcoming else ""

    # 调用 agent.py 中真正的发送函数，注意参数顺序需要匹配
    return _send_email(receive_email, score, job_title, apply_result, report, short_adv, short_short)


# ==================== 8. 存入数据库（直接复用 agent.py） ====================
def handle_save_to_db(detail_data):
    """将简历评分结果写入 MySQL（resume_record 表）"""
    return _save_to_mysql(detail_data)

# ==================== 9. 写业务日志（直接复用 agent.py） ====================
def handle_log(resume_name, job_name, score, email, mail_status, result_status):
    """将投递、评分结果写入 log_dayinfo 日志文件"""
    _write_recruit_log(
        resume_name=resume_name,
        job_name=job_name,
        score=score,
        email=email,
        mail_status=mail_status,
        result_status=result_status
    )


# ==================== 10. 自由对话（规则兜底调用大模型） ====================
def generate_free_reply(history_list, user_input):
    """
    当意图路由未匹配到任何关键词时，调用大模型生成智能回复。
    传入完整的对话历史（最近6条）和用户最新输入，让大模型理解上下文并给予友好引导。
    """
    recent = history_list[-6:] if len(history_list) > 6 else history_list
    history_text = "\n".join(
        [f"{'用户' if m['role']=='user' else '助手'}: {m['content']}" for m in recent]
    )

    prompt = f"""你是一个专业的智聘未来招聘助手。根据对话历史, 用自然、友好的语气回应用户, 
并尝试引导用户使用以下功能:
- 查看在招岗位
- 了解岗位具体要求
- 上传简历
- 评估简历与岗位的匹配度
- 获取简历优化建议

不要编造虚构信息。如果用户想了解岗位, 提醒他们可以直接说出岗位名称。
当前对话历史:
{history_text}
用户最新输入: {user_input}

请直接给出助手回复:"""

    return call_llm([{"role": "user", "content": prompt}], temperature=0.7)
# ==================== 11. 面试链接生成与校验 ====================
def generate_interview_token(email, resume_name, job_name):
    """
    生成唯一的面试加密token（基于邮箱+简历名+时间戳+随机盐）
    返回：加密字符串token
    """
    raw = f"{email}_{resume_name}_{job_name}_{datetime.now().timestamp()}_{secrets.token_hex(8)}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    return token


def create_interview_link(email, resume_name, job_name, resume_record_id):
    token = generate_interview_token(email, resume_name, job_name)
    expired_at = datetime.now() + timedelta(hours=48)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = """INSERT INTO interview_record 
                     (candidate_name, email, resume_id, job_name, token, status, expired_at, resume_record_id)
                     VALUES (%s, %s, %s, %s, %s, 'pending', %s, %s)"""
            cur.execute(sql, (email.split('@')[0], email, resume_name, job_name, token, expired_at, resume_record_id))
        conn.commit()
    except Exception as e:
        print(f"❌ 创建面试记录失败: {e}")
        return None
    finally:
        conn.close()

    base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
    interview_url = f"{base_url}/interview_page?token={token}"
    return interview_url

def verify_interview_token(token):
    """
    校验面试token是否有效
    返回：(is_valid, record_dict, message)
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = "SELECT * FROM interview_record WHERE token=%s"
            cur.execute(sql, (token,))
            record = cur.fetchone()

            if not record:
                return False, None, "无效的面试链接，请检查链接是否正确。"

            if record['status'] == 'completed':
                return False, None, "该面试已经完成，不可重复进入。"

            if record['status'] == 'expired':
                return False, None, "该面试链接已过期失效。"

            if datetime.now() > record['expired_at']:
                # 过期了，更新状态
                cur.execute("UPDATE interview_record SET status='expired' WHERE token=%s", (token,))
                conn.commit()
                return False, None, "面试链接已过期（48小时有效期），请联系HR重新发起面试。"

            return True, record, "验证通过"
    except Exception as e:
        return False, None, f"验证异常: {e}"
    finally:
        conn.close()


def update_interview_status(token, status):
    """更新面试状态"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if status == 'completed':
                cur.execute("UPDATE interview_record SET status=%s, completed_at=NOW() WHERE token=%s", (status, token))
            else:
                cur.execute("UPDATE interview_record SET status=%s WHERE token=%s", (status, token))
        conn.commit()
    except Exception as e:
        print(f"❌ 更新面试状态失败: {e}")
    finally:
        conn.close()


def read_resume_text_from_file(filepath):
    """读取简历文本，供面试页调用（兼容旧函数名）"""
    from agent import read_resume_text as _read
    return _read(filepath)


# ==================== 12. 面试模块题目生成与评分 ====================
MODULE_NAMES = ["基础知识", "项目经历", "实习经历", "技能实战", "技能进阶实战"]
MODULE_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]
QUESTIONS_PER_MODULE = [2, 3, 3, 2, 2]

def generate_questions_for_module(module_name, resume_text, jd_content):
    """
    生成模块面试题，并带参考答案和评分要点。
    返回 JSON 列表，每项包含 question, reference_answer, scoring_points
    """
    # 从简历中抽取关键技术词（简单正则）
    tech_keywords = []
    for kw in ["Python", "Java", "C\\+\\+", "Go", "React", "Vue", "Spring", "Django",
               "TensorFlow", "PyTorch", "Spark", "Flink", "Hadoop", "Hive", "MySQL",
               "Redis", "MongoDB", "Docker", "Kubernetes", "Linux", "Git", "SQL",
               "机器学习", "深度学习", "NLP", "计算机视觉", "数据分析", "数据挖掘"]:
        if re.search(kw, resume_text, re.IGNORECASE):
            tech_keywords.append(kw)
    tech_str = "、".join(tech_keywords[:6]) if tech_keywords else "Python, SQL"

    base_prompt = f"""你是一位资深技术面试官。请根据候选人简历和岗位JD，设计{QUESTIONS_PER_MODULE[MODULE_NAMES.index(module_name)]}道面试题。

【当前模块】{module_name}
【候选人技术栈】{tech_str}
【简历摘要】{resume_text[:1200]}
【岗位JD】{jd_content[:600]}

【出题要求】
1. 题目必须紧扣候选人的技术栈和简历中的具体经历，不得泛泛而谈。
2. 对每道题提供参考答案（50字以内要点）和3个评分要点。
3. 返回严格 JSON 格式，不含任何额外文字。

JSON 格式示例：
[
  {{
    "question": "题目内容",
    "reference_answer": "参考答案要点",
    "scoring_points": ["要点1", "要点2", "要点3"]
  }}
]"""

    # 各模块补充性约束
    module_extra = {
        "基础知识": f"请围绕 {tech_str} 的核心原理、常见坑点出题，题目如“{tech_keywords[0] if tech_keywords else 'Python'} 的垃圾回收机制是什么？”",
        "技能实战": "请设计一个基于候选人技术栈的实际工作场景问题，考察解决问题的思路和工具选择。",
        "技能进阶实战": "请考察候选人对高并发、分布式、性能优化等进阶话题的理解，题目需结合其技术栈。"
    }
    extra = module_extra.get(module_name, "")
    prompt = base_prompt + "\n" + extra

    content = call_llm([{"role":"user","content":prompt}], temperature=0.7)
    try:
        questions = json.loads(content)
        # 确保格式完整
        for q in questions:
            q.setdefault("reference_answer", "")
            q.setdefault("scoring_points", [])
        return questions[:QUESTIONS_PER_MODULE[MODULE_NAMES.index(module_name)]]
    except:
        # 降级：生成占位题，但带上提示
        return [{
            "question": f"请介绍您在{module_name}方面的理解或经验。",
            "reference_answer": "根据简历及岗位要求进行评估",
            "scoring_points": ["回答相关", "逻辑清晰", "有实例"]
        }]
def score_interview(token, all_answers, record):
    """
    对面试答案进行5模块评分，存入数据库，发送双端邮件
    """
    scores = {}
    # 按模块分组答案
    module_answers = {}
    for ans in all_answers:
        mod = ans['module']
        module_answers.setdefault(mod, []).append(ans)

        for module_name, answers_list in module_answers.items():
            eval_items = []
            for ans in answers_list:
                # 从存储的题目中获取参考答案和评分点
                question_text = ans['question']
                # 如果题目结构里已包含评分点（来自 generate_questions_for_module）
                ref_answer = ans.get('reference_answer', '')
                scoring_points = ans.get('scoring_points', [])

                eval_items.append({
                    "question": question_text,
                    "user_answer": ans['answer'],
                    "reference_answer": ref_answer,
                    "scoring_points": scoring_points
                })

            # 构建评分 prompt
            eval_json = json.dumps(eval_items, ensure_ascii=False)
            score_prompt = f"""你是面试官。请对以下{module_name}模块的每个问答，逐一评分（1-10分），并给出简短评语。

        岗位：{record['job_name']}

        问答详情（含参考答案和评分点）：
        {eval_json}

        请返回 JSON 对象，包含每个问题的评分和模块总分（取平均）。格式：
        {{
          "items": [
            {{"question": "题面", "score": 8, "comment": "理由"}}
          ],
          "module_score": 7.5
        }}"""
            content = call_llm([{"role": "user", "content": score_prompt}], temperature=0.2)
            try:
                result_data = json.loads(content)
                scores[module_name] = result_data["module_score"]
            except:
                scores[module_name] = 6  # 降级

    # 加权计算总分
    total = sum(scores.get(m, 6) * MODULE_WEIGHTS[i] for i, m in enumerate(MODULE_NAMES))
    apply_result = "录用" if total >= 7 else "不合适"

    # 存入MySQL
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = """UPDATE interview_record SET 
                     score_basic=%s, score_project=%s, score_intern=%s, 
                     score_practice=%s, score_advanced=%s, total_score=%s,
                     answers=%s, apply_result=%s, completed_at=NOW()
                     WHERE token=%s"""
            cur.execute(sql, (
                scores.get('基础知识', 0),
                scores.get('项目经历', 0),
                scores.get('实习经历', 0),
                scores.get('技能实战', 0),
                scores.get('技能进阶实战', 0),
                total,
                json.dumps(all_answers, ensure_ascii=False),
                apply_result,
                token
            ))
        conn.commit()
    except Exception as e:
        print(f"❌ 面试数据入库失败: {e}")
    finally:
        conn.close()

    # 发送双端邮件
    send_interview_emails(record['email'], record['job_name'], scores, total, apply_result, all_answers)

    update_excel_interview_scores(record['resume_record_id'], scores, total, apply_result)
    # 写日志
    handle_log(record['resume_id'], record['job_name'], total, record['email'], '已面试', apply_result)


def update_excel_interview_scores(record_id, scores, total, apply_result):
    excel_path = r"F:\ai智能招聘系统_参赛项目\04_数据文件\recruitment_data.xlsx"
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"🔔 开始更新 Excel 面试分数，ID={record_id}, Sheet={today_str}", flush=True)

    try:
        if not os.path.exists(excel_path):
            print(f"❌ Excel 文件不存在：{excel_path}")
            return

        df = pd.read_excel(excel_path, sheet_name=today_str)
        df["ID_str"] = df["ID"].astype(str)
        mask = df["ID_str"] == str(record_id)
        print(f"🔍 查找 ID={record_id}，匹配行数：{mask.sum()}", flush=True)

        if mask.any():
            idx = df[mask].index[0]

            # 将要更改的列全部转成字符串，避免 dtype 不兼容
            for col in ["是否进行AI面试", "是否录用", "基础知识得分", "项目经历得分", "实习经历得分", "技能实战得分", "进阶实战得分", "总分"]:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            df.at[idx, "是否进行AI面试"] = "是"
            df.at[idx, "基础知识得分"] = str(scores.get("基础知识", 0))
            df.at[idx, "项目经历得分"] = str(scores.get("项目经历", 0))
            df.at[idx, "实习经历得分"] = str(scores.get("实习经历", 0))
            df.at[idx, "技能实战得分"] = str(scores.get("技能实战", 0))
            df.at[idx, "进阶实战得分"] = str(scores.get("技能进阶实战", 0))
            df.at[idx, "总分"] = str(total)
            df.at[idx, "是否录用"] = apply_result

            # 删除临时列
            df.drop(columns=["ID_str"], inplace=True)

            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=today_str, index=False)
            print(f"✅ Excel 面试分数已更新，ID={record_id}", flush=True)
        else:
            print(f"⚠️ 未在 Excel 中找到 ID={record_id}，请检查 Excel 中的 ID 列与传入值", flush=True)
    except Exception as e:
        import traceback
        print(f"❌ 更新 Excel 面试得分失败: {e}")
        traceback.print_exc()
def send_interview_emails(email, job_name, scores, total, apply_result, all_answers):
    """面试结果双端邮件"""
    from agent import send_interview_result_email
    send_interview_result_email(email, job_name, scores, total, apply_result, all_answers)

def send_invitation_email(email, candidate_name, interview_url):
    """调用 agent.py 发送面试邀请邮件"""
    from agent import send_interview_invitation_email
    return send_interview_invitation_email(email, candidate_name, interview_url)
MODULE_FIELD_MAP = {
    "基础知识": "questions_basic",
    "项目经历": "questions_project",
    "实习经历": "questions_intern",
    "技能实战": "questions_practice",
    "技能进阶实战": "questions_advanced",
}

def update_module_questions(token, module_name, questions_json):
    field = MODULE_FIELD_MAP.get(module_name)
    if not field:
        return
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = f"UPDATE interview_record SET {field}=%s WHERE token=%s"
            cur.execute(sql, (json.dumps(questions_json, ensure_ascii=False), token))
        conn.commit()
    except Exception as e:
        print(f"更新面试题目字段 {field} 失败: {e}")
    finally:
        conn.close()


def handle_save_to_excel(detail_data):
    excel_path = r"F:\ai智能招聘系统_参赛项目\04_数据文件\recruitment_data.xlsx"
    today_str = datetime.now().strftime("%Y-%m-%d")

    row = {
        "ID": detail_data.get("ID", ""),
        "投递时间": detail_data.get("投递时间", ""),
        "姓名": detail_data.get("姓名", ""),
        "性别": detail_data.get("性别", ""),
        "年龄": detail_data.get("年龄", ""),
        "学历": detail_data.get("学历", ""),
        "投递岗位": detail_data.get("岗位", ""),
        "所在城市": detail_data.get("所在城市", ""),
        "意向城市": detail_data.get("意向地区", ""),
        "简历得分": detail_data.get("得分", 0),
        "是否通过初筛": "是" if detail_data.get("测评结果") == "录用" else "否",
        "是否进行AI面试": "",
        "基础知识得分": "",
        "项目经历得分": "",
        "实习经历得分": "",
        "技能实战得分": "",
        "进阶实战得分": "",
        "总分": "",
        "是否录用": ""
    }

    df_new = pd.DataFrame([row])
    # 强制指定所有列为字符串类型（数值列保留原类型，其余转 str）
    for col in ["是否进行AI面试", "是否录用", "基础知识得分", "项目经历得分", "实习经历得分", "技能实战得分", "进阶实战得分", "总分"]:
        df_new[col] = df_new[col].astype(str)

    try:
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        if os.path.exists(excel_path):
            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                if today_str in writer.sheets:
                    df_old = pd.read_excel(excel_path, sheet_name=today_str)
                    # 将旧数据的这些列也转为 str，避免后续 concat 时报类型不兼容
                    for col in df_new.columns:
                        if col in df_old.columns and df_new[col].dtype == object:
                            df_old[col] = df_old[col].astype(str)
                    df_combined = pd.concat([df_old, df_new], ignore_index=True)
                    df_combined.to_excel(writer, sheet_name=today_str, index=False)
                else:
                    df_new.to_excel(writer, sheet_name=today_str, index=False)
        else:
            df_new.to_excel(excel_path, sheet_name=today_str, index=False)
        print(f"✅ 数据已写入 Excel：{excel_path} → Sheet: {today_str}")
    except Exception as e:
        import traceback
        print(f"❌ Excel 写入失败: {e}")
        traceback.print_exc()