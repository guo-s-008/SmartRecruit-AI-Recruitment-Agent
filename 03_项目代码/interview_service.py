

"""
面试服务模块
负责面试相关的所有功能 - 自动切换SQLite和MySQL
"""
from config import USE_SQLITE

if USE_SQLITE:
    from interview_service_sqlite import (
        create_interview_token,
        create_interview_link,
        verify_interview_token,
        update_interview_status,
        update_module_questions,
        generate_questions_for_module,
        generate_default_questions,
        score_interview
    )
else:
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

    def create_interview_token(email, resume_name, job_name):
        """
        创建面试token
        """
        raw = f"{email}{resume_name}{job_name}{datetime.now().timestamp()}"
        token = hashlib.md5(raw.encode()).hexdigest() + secrets.token_hex(8)
        return token

    def create_interview_link(email, resume_name, job_name, resume_id=None, candidate_name=''):
        """
        创建面试链接
        :param email: 候选人邮箱
        :param resume_name: 简历名称
        :param job_name: 岗位名称
        :param resume_id: 简历ID（可选）
        :param candidate_name: 候选人姓名（可选）
        :return: 面试链接
        """
        token = create_interview_token(email, resume_name, job_name)
        expired_at = datetime.now() + timedelta(hours=INTERVIEW_CONFIG["token_expire_hours"])

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO interview_record 
                    (token, email, candidate_name, resume_name, job_name, resume_id, status, created_at, expired_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (token, email, candidate_name, resume_name, job_name, str(resume_id) if resume_id else None, 
                      'pending', datetime.now(), expired_at))
            conn.commit()
            conn.close()

            return f"{APP_BASE_URL}/pages/interview_page.py?token={token}"
        except Exception as e:
            print(f"创建面试链接失败: {e}")
            return None

    def verify_interview_token(token):
        """
        验证面试token
        :param token: 面试token
        :return: (is_valid, record, message)
        """
        try:
            conn = get_db_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM interview_record WHERE token=%s", (token,))
                record = cur.fetchone()

                if not record:
                    return False, None, "面试链接无效，请检查链接是否正确。"

                if record['status'] == 'completed':
                    return False, None, "该面试已经完成，不可重复进入。"

                if record['status'] == 'expired':
                    return False, None, "该面试链接已过期失效。"

                if datetime.now() > record['expired_at']:
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
        :param status: 状态值
        """
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("UPDATE interview_record SET status=%s, updated_at=%s WHERE token=%s",
                            (status, datetime.now(), token))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"更新面试状态失败: {e}")

    def update_module_questions(token, module_name, questions):
        """
        更新面试题目记录
        :param token: 面试token
        :param module_name: 模块名称
        :param questions: 题目列表
        """
        field_name = MODULE_FIELD_MAP.get(module_name)
        if not field_name:
            return

        questions_json = json.dumps(questions, ensure_ascii=False)

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(f"UPDATE interview_record SET {field_name}=%s WHERE token=%s",
                            (questions_json, token))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"更新面试题目失败: {e}")

    def generate_questions_for_module(module_name, resume_text, jd_content):
        """
        为指定模块生成面试题
        :param module_name: 模块名称
        :param resume_text: 简历文本
        :param jd_content: JD内容
        :return: 题目列表
        """
        questions_num = QUESTIONS_PER_MODULE

        # 根据不同模块，定制不同的提示词
        module_specific_instructions = {
            "项目经历": "请重点围绕简历中提到的具体项目进行深度提问，比如技术难点、解决方案、个人贡献等。",
            "实习经历": "请围绕实习期间的工作内容、收获和成长进行提问。",
            "基础知识": "结合岗位JD和简历背景，考察相关的基础知识。",
            "技能实战": "围绕岗位所需技能和简历中提到的技能，设计场景化问题。",
            "技能进阶实战": "考察候选人的技术深度、学习能力和未来规划。"
        }
        
        instruction = module_specific_instructions.get(module_name, "根据JD和简历进行针对性提问。")
        
        prompt = f"""你是一位资深技术面试官，请根据以下岗位JD和候选人简历，为【{module_name}】模块生成{questions_num}道面试题。

【重要要求】
- 问题必须紧密结合候选人简历中的具体内容！
- 如果是项目经历模块，请直接针对简历中提到的项目进行提问！
- 如果是实习经历模块，请直接针对简历中提到的实习内容提问！
- {instruction}

【岗位JD】
{jd_content}

【候选人简历】
{resume_text[:2500]}

请按照以下JSON格式输出：
[
  {{\"question\": \"问题内容\", \"reference_answer\": \"参考答案要点\", \"scoring_points\": [\"评分点1\", \"评分点2\"]}},
  ...
]"""

        try:
            response = call_llm([{"role": "user", "content": prompt}], temperature=0.3)
            questions = json.loads(response)
            return questions[:questions_num]
        except Exception as e:
            print(f"生成面试题失败: {e}")
            return generate_default_questions(module_name)

    def generate_default_questions(module_name):
        """
        生成默认面试题
        """
        defaults = {
            "基础知识": [
                {"question": "请介绍一下你所学专业的核心课程有哪些？", "reference_answer": "列举3-5门核心课程", "scoring_points": ["课程相关性", "理解深度"]},
                {"question": "你掌握的编程语言有哪些？请举例说明项目中如何使用的。", "reference_answer": "列举编程语言及应用场景", "scoring_points": ["技术栈广度", "实际应用能力"]},
                {"question": "数据库的ACID特性是什么？请简要解释。", "reference_answer": "原子性、一致性、隔离性、持久性", "scoring_points": ["概念理解"]}
            ],
            "项目经历": [
                {"question": "请介绍你参与过的最有代表性的项目。", "reference_answer": "项目背景、职责、成果", "scoring_points": ["项目复杂度", "个人贡献"]},
                {"question": "项目中遇到的最大挑战是什么？如何解决的？", "reference_answer": "问题描述、解决方案、结果", "scoring_points": ["问题分析能力", "解决能力"]},
                {"question": "你在项目中的角色是什么？有哪些具体贡献？", "reference_answer": "角色定位、具体成果", "scoring_points": ["职责清晰", "贡献量化"]}
            ],
            "实习经历": [
                {"question": "你在实习期间主要负责什么工作？", "reference_answer": "职责描述、工作内容", "scoring_points": ["职责匹配度", "工作深度"]},
                {"question": "实习期间学到了哪些最有价值的技能？", "reference_answer": "技能描述、应用场景", "scoring_points": ["技能收获", "实际应用"]}
            ],
            "技能实战": [
                {"question": "请描述一次你解决技术难题的经历。", "reference_answer": "问题、思路、方案、结果", "scoring_points": ["问题分析", "技术能力"]},
                {"question": "你最擅长的技术领域是什么？为什么？", "reference_answer": "技术领域、掌握程度、应用经验", "scoring_points": ["专业深度", "实践经验"]},
                {"question": "如何保证代码质量？你通常会做哪些检查？", "reference_answer": "代码审查、测试、规范", "scoring_points": ["质量意识", "方法论"]}
            ],
            "技能进阶实战": [
                {"question": "你对未来的技术发展方向有什么规划？", "reference_answer": "短期目标、长期规划", "scoring_points": ["规划清晰", "可行性"]},
                {"question": "如果遇到技术瓶颈，你会如何突破？", "reference_answer": "学习方法、解决路径", "scoring_points": ["学习能力", "解决策略"]},
                {"question": "你如何看待技术创新与业务需求之间的关系？", "reference_answer": "平衡观点、实际案例", "scoring_points": ["大局观", "实践理解"]}
            ]
        }
        return defaults.get(module_name, [{"question": "请自我介绍一下", "reference_answer": "个人介绍", "scoring_points": ["表达能力"]}])

    def score_interview(token, answers, record):
        """
        评分面试答案
        :param token: 面试token
        :param answers: 答案列表
        :param record: 面试记录
        """
        try:
            all_scores = []
            for module in MODULE_NAMES:
                module_answers = [a for a in answers if a['module'] == module]
                if not module_answers:
                    continue

                module_score = 0
                for ans in module_answers:
                    question = ans['question']
                    answer = ans['answer']
                    scoring_points = ans.get('scoring_points', [])

                    prompt = f"请根据以下面试题和候选人回答进行评分（满分10分）。\n\n【问题】{question}\n【候选人回答】{answer}\n【评分要点】{', '.join(scoring_points)}\n\n请直接给出分数（仅数字），并简要说明理由。"
                    response = call_llm([{"role": "user", "content": prompt}], temperature=0.1)

                    match = re.search(r'(\d+)', response)
                    if match:
                        module_score += int(match.group(1))

                avg_score = module_score / len(module_answers)
                all_scores.append((module, avg_score))

            total_score = sum(s[1] * MODULE_WEIGHTS[i] / 10 for i, s in enumerate(all_scores))
            apply_result = "录用" if total_score >= 8 else "不合适"

            send_interview_result_email(record['email'], record['job_name'], dict(all_scores), round(total_score, 1), apply_result, answers)

            update_excel_interview_scores(record['email'], record['job_name'], round(total_score, 1), apply_result)

            update_interview_status(token, 'completed')

            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("UPDATE interview_record SET final_score=%s, result=%s WHERE token=%s",
                                (round(total_score, 1), apply_result, token))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"更新面试结果失败: {e}")

        except Exception as e:
            print(f"面试评分失败: {e}")

