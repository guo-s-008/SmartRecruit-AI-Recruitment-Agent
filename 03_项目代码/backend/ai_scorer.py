
"""
AI 评分模块
调用阿里云百炼大模型进行简历评分和智能对话
"""
import re
import json
import requests
from config import API_CONFIG


def call_llm(messages, temperature=0.3):
    """
    调用阿里云百炼大模型 API
    :param messages: 对话消息列表
    :param temperature: 温度参数
    :return: 模型回复内容
    """
    headers = {
        "Authorization": f"Bearer {API_CONFIG['key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": API_CONFIG['model'],
        "messages": messages,
        "temperature": temperature
    }
    try:
        resp = requests.post(API_CONFIG['url'], headers=headers, json=payload, timeout=35)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) &gt; 0:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API返回异常：{data}"
    except Exception as e:
        return f"AI调用失败：{str(e)}"


def ai_score_resume_with_jd(resume_text, jd_content, job_name="匹配到的岗位"):
    """
    根据 JD 对简历进行 AI 评分
    :param resume_text: 简历文本
    :param jd_content: JD 内容
    :param job_name: 岗位名称
    :return: (分数, 完整报告)
    """
    prompt = f"""你是专业HR面试官，根据【岗位JD】对简历进行严格评分（满分100）。

【岗位名称】
{job_name}

【岗位JD要求】
{jd_content}

【简历内容】
{resume_text[:3000]}

请严格按以下格式输出：

【简历评分】
分数：xx

【分项评分标准】
1. 专业匹配度：xx分
2. 技能匹配度：xx分
3. 项目经验匹配度：xx分
4. 综合素养：xx分

【简历优势】
xxx

【简历不足与改进建议】
xxx
"""

    headers = {
        "Authorization": f"Bearer {API_CONFIG['key']}",
        "Content-Type": "application/json"
    }

    data = {
        "model": API_CONFIG['model'],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    try:
        response = requests.post(API_CONFIG['url'], headers=headers, json=data, timeout=35)
        res_json = response.json()

        if "choices" in res_json:
            content = res_json["choices"][0]["message"]["content"]
        else:
            content = f"AI返回异常：{str(res_json)}"
    except Exception as e:
        content = f"AI调用失败：{str(e)}"
        score = 0
        return score, content

    score = 0
    num_list = re.findall(r"分数[:：]\s*(\d+)", content)
    if num_list:
        score = int(num_list[0])

    if score &gt;= 85:
        final_msg = f"""
——————————————
【录用结果通知】
恭喜同学，你的简历综合得分：{score}分，
你的简历符合岗位录用标准，
欢迎加入智聘未来团队，
后续将通过邮件通知面试安排，请耐心等待。
"""
    else:
        final_msg = f"""
——————————————
【录用结果通知】
很遗憾，你的简历综合得分：{score}分，
暂时与岗位要求存在差距，
建议结合改进建议优化简历，
欢迎再次投递。
"""

    return score, content + final_msg


def handle_score(job_name, resume_text, jd_content, scoring_criteria=""):
    """
    结构化 AI 评分，返回结构化数据
    :param job_name: 岗位名称
    :param resume_text: 简历文本
    :param jd_content: JD 内容
    :param scoring_criteria: 评分标准（可选）
    :return: {score, report, advantage, shortcoming}
    """
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
- 具体列出与JD匹配的亮点，每条用"- "开头，至少写3条，要结合简历中的具体内容
- 每条优势都要有具体的技能/项目/经验支撑

【简历不足与改进建议】
- 具体列出与JD要求有明显差距的地方，每条用"- "开头，至少写3条
- 针对每条不足给出可操作的改进建议

在报告最后，额外返回一个 JSON 片段（仅此片段，不要混入正文）：
{{"short_advantage": "简历优点摘要（50字以内，用于网页快速展示）", "short_shortcoming": "简历不足摘要（50字以内，用于网页快速展示）"}}
"""
    content = call_llm([{"role": "user", "content": prompt}], temperature=0.1)

    short_advantage = ""
    short_shortcoming = ""
    full_report = content

    lines = content.strip().split("\n")
    json_str = None
    for line in reversed(lines):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            json_str = line
            break

    if not json_str:
        try:
            start = content.rfind("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end &gt; start:
                json_str = content[start:end + 1]
        except:
            pass

    if json_str:
        try:
            short_data = json.loads(json_str)
            short_advantage = short_data.get("short_advantage", "")
            short_shortcoming = short_data.get("short_shortcoming", "")
            full_report = content.replace(json_str, "").strip()
        except:
            pass

    score = 0
    match = re.findall(r"分数[：:]\s*(\d+)", full_report)
    if match:
        score = int(match[0])

    if not short_advantage:
        if "【简历优势】" in full_report:
            parts = full_report.split("【简历优势】")[-1].split("【简历不足与改进建议】")
            short_advantage = parts[0].strip()[:100] if parts else ""
    if not short_shortcoming:
        if "【简历不足与改进建议】" in full_report:
            parts = full_report.split("【简历不足与改进建议】")[-1].split("——————————————")
            short_shortcoming = parts[0].strip()[:100]

    if not short_advantage:
        short_advantage = "简历与岗位要求基本匹配"
    if not short_shortcoming:
        short_shortcoming = "建议补充项目量化成果与核心技能"

    return {
        "score": score,
        "report": full_report,
        "advantage": short_advantage,
        "shortcoming": short_shortcoming
    }


def ask_resume_question(resume_text, question):
    """
    根据简历内容回答用户问题
    :param resume_text: 简历文本
    :param question: 用户问题
    :return: AI 回复
    """
    prompt = f"""你是一位专业招聘顾问，根据候选人简历内容回答其问题。

【简历内容】
{resume_text[:2000]}

【候选人问题】
{question}

请给出具体、有针对性、可操作的回答。如果简历中缺乏相关信息，也请诚实指出。"""
    return call_llm([{"role": "user", "content": prompt}], temperature=0.5)


def generate_free_reply(history_list, user_input):
    """
    生成自由对话回复
    :param history_list: 对话历史列表
    :param user_input: 用户最新输入
    :return: AI 回复
    """
    recent = history_list[-6:] if len(history_list) &gt; 6 else history_list
    history_text = "\n".join(
        [f"{'用户' if m['role'] == 'user' else '助手'}: {m['content']}" for m in recent]
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

