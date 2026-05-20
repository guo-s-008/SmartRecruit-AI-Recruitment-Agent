
"""
面试服务模块
负责面试相关的所有功能
"""
import re
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from config import APP_BASE_URL, INTERVIEW_CONFIG
from database import get_db_connection
from ai_scorer import call_llm
from email_service import send_interview_result_email, send_interview_invitation_email
from excel_service import update_excel_interview_scores


MODULE_NAMES = INTERVIEW_CONFIG["module_names"]
MODULE_WEIGHTS = INTERVIEW_CONFIG["module_weights"]
QUESTIONS_PER_MODULE = INTERVIEW_CONFIG["questions_per_module"]
MODULE_FIELD_MAP = {
    "基础知识": "questions_basic",
    "项目经历": "questions_project",
    "实习经历": "questions_intern",
    "技能实战": "questions_practice",
    "技能进阶实战": "questions_advanced",
}


def generate_interview_token(email, resume_name, job_name):
    """
    生成面试 token
    :param email: 邮箱
    :param resume_name: 简历文件名
    :param job_name: 岗位名称
    :return: token
    """
    raw = f"{email}_{resume_name}_{job_name}_{datetime.now().timestamp()}_{secrets.token_hex(8)}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    return token


def create_interview_link(email, resume_name, job_name, resume_record_id):
    """
    创建面试链接
    :param email: 邮箱
    :param resume_name: 简历文件名
    :param job_name: 岗位名称
    :param resume_record_id: 简历记录ID
    :return: 面试链接，失败返回None
    """
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

    interview_url = f"{APP_BASE_URL}/interview_page?token={token}"
    return interview_url


def verify_interview_token(token):
    """
    验证面试 token
    :param token: 面试token
    :return: (是否有效, 记录字典, 消息)
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

            if datetime.now() &gt; record['expired_at']:
                cur.execute("UPDATE interview_record SET status='expired' WHERE token=%s", (token,))
                conn.commit()
                return False, None, "面试链接已过期（48小时有效期），请联系HR重新发起面试。"

            return True, record, "验证通过"
    except Exception as e:
        return False, None, f"验证异常: {e}"
    finally:
        conn.close()


def update_interview_status(token, status):
    """
    更新面试状态
    :param token: 面试token
    :param status: 状态
    """
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


def generate_questions_for_module(module_name, resume_text, jd_content):
    """
    为某个模块生成面试题
    :param module_name: 模块名称
    :param resume_text: 简历文本
    :param jd_content: JD内容
    :return: 题目列表
    """
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

    module_extra = {
        "基础知识": f"请围绕 {tech_str} 的核心原理、常见坑点出题，题目如\"{tech_keywords[0] if tech_keywords else 'Python'} 的垃圾回收机制是什么？\"",
        "技能实战": "请设计一个基于候选人技术栈的实际工作场景问题，考察解决问题的思路和工具选择。",
        "技能进阶实战": "请考察候选人对高并发、分布式、性能优化等进阶话题的理解，题目需结合其技术栈。"
    }
    extra = module_extra.get(module_name, "")
    prompt = base_prompt + "\n" + extra

    content = call_llm([{"role": "user", "content": prompt}], temperature=0.7)
    try:
        questions = json.loads(content)
        for q in questions:
            q.setdefault("reference_answer", "")
            q.setdefault("scoring_points", [])
        return questions[:QUESTIONS_PER_MODULE[MODULE_NAMES.index(module_name)]]
    except:
        return [{
            "question": f"请介绍您在{module_name}方面的理解或经验。",
            "reference_answer": "根据简历及岗位要求进行评估",
            "scoring_points": ["回答相关", "逻辑清晰", "有实例"]
        }]


def update_module_questions(token, module_name, questions_json):
    """
    更新模块题目到数据库
    :param token: 面试token
    :param module_name: 模块名称
    :param questions_json: 题目JSON
    """
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


def score_interview(token, all_answers, record):
    """
    对面试进行评分
    :param token: 面试token
    :param all_answers: 所有答案
    :param record: 面试记录
    """
    scores = {}
    module_answers = {}
    for ans in all_answers:
        mod = ans['module']
        module_answers.setdefault(mod, []).append(ans)

    for module_name, answers_list in module_answers.items():
        eval_items = []
        for ans in answers_list:
            question_text = ans['question']
            ref_answer = ans.get('reference_answer', '')
            scoring_points = ans.get('scoring_points', [])

            eval_items.append({
                "question": question_text,
                "user_answer": ans['answer'],
                "reference_answer": ref_answer,
                "scoring_points": scoring_points
            })

        eval_json = json.dumps(eval_items, ensure_ascii=False)
        score_prompt = f"""你是面试官。请对以下{module_name}模块的每个问答，逐一评分（1-10分），并给出简短评语。

岗位：{record['job_name']}

问答详情（含参考答案和评分要点）：
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
            scores[module_name] = 6

    total = sum(scores.get(m, 6) * MODULE_WEIGHTS[i] for i, m in enumerate(MODULE_NAMES))
    apply_result = "录用" if total &gt;= 7 else "不合适"

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

    send_interview_result_email(record['email'], record['job_name'], scores, total, apply_result, all_answers)

    update_excel_interview_scores(record['resume_record_id'], scores, total, apply_result)

    from log_system import write_recruit_log
    write_recruit_log(
        resume_name=record['resume_id'],
        job_name=record['job_name'],
        score=total,
        email=record['email'],
        mail_status='已面试',
        result_status=apply_result
    )

