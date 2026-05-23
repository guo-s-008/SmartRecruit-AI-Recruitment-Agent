
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
    if not API_CONFIG['key'] or API_CONFIG['key'] == 'your_api_key_here':
        return "⚠️ 错误：未配置大模型 API Key\n\n请在【04_数据文件/.env】文件中配置有效的 API_KEY，或联系管理员获取。"
    
    headers = {
        "Authorization": "Bearer " + API_CONFIG['key'],
        "Content-Type": "application/json"
    }
    
    # 适配阿里云百炼API v1格式
    payload = {
        "model": API_CONFIG['model'],
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": temperature
        }
    }
    
    try:
        resp = requests.post(API_CONFIG['url'], headers=headers, json=payload, timeout=35)
        resp.raise_for_status()
        data = resp.json()
        
        if "output" in data and "text" in data["output"]:
            return data["output"]["text"]
        elif "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            return "API返回异常：" + str(data)
    except Exception as e:
        return "AI调用失败：" + str(e)


def ai_score_resume_with_jd(resume_text, jd_content, job_name="匹配到的岗位"):
    """
    根据 JD 对简历进行 AI 评分
    :param resume_text: 简历文本
    :param jd_content: JD 内容
    :param job_name: 岗位名称
    :return: (分数, 完整报告)
    """
    prompt = "你是专业HR面试官，根据【岗位JD】对简历进行严格评分（满分100）。\n\n【岗位名称】\n" + job_name + "\n\n【岗位JD要求】\n" + jd_content + "\n\n【简历内容】\n" + resume_text[:3000] + "\n\n请严格按以下格式输出：\n\n【简历评分】\n分数：xx\n\n【分项评分标准】\n1. 专业匹配度：xx分\n2. 技能匹配度：xx分\n3. 项目经验匹配度：xx分\n4. 综合素养：xx分\n\n【简历优势】\nxxx\n\n【简历不足与改进建议】\nxxx"

    headers = {
        "Authorization": "Bearer " + API_CONFIG['key'],
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
            content = "AI返回异常：" + str(res_json)
    except Exception as e:
        content = "AI调用失败：" + str(e)
        score = 0
        return score, content

    score = 0
    num_list = re.findall(r"分数[:：]\s*(\d+)", content)
    if num_list:
        score = int(num_list[0])

    if score >= 70:
        final_msg = "\n——————————————\n【初筛结果通知】\n恭喜同学，你的简历综合得分：" + str(score) + "分，\n你的简历通过了初筛！\n后续将通过邮件发送面试邀请，请留意邮箱。"
    else:
        final_msg = "\n——————————————\n【初筛结果通知】\n很遗憾，你的简历综合得分：" + str(score) + "分，\n暂未通过初筛，\n建议结合改进建议优化简历，\n欢迎再次投递。"

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
    criteria_text = scoring_criteria if scoring_criteria else "请按专业匹配度、技能匹配度、项目经验匹配度、学历/经验匹配度四个维度自主评分，满分100。"
    prompt = "你是专业HR面试官，请根据【岗位JD】和【评分标准】对候选人简历进行严格评分（满分100）。\n\n【岗位名称】" + job_name + "\n【岗位JD要求】" + jd_content + "\n【评分标准】" + criteria_text + "\n\n【简历内容】" + resume_text[:3000] + "\n\n请严格按照以下格式输出完整的评分报告（这个报告将直接作为邮件正文发送给求职者，请务必详细、专业）：\n\n【简历评分】\n分数：xx\n\n【分项评分标准】\n1. 专业匹配度：xx分\n2. 技能匹配度：xx分\n3. 项目经验匹配度：xx分\n4. 综合素养：xx分\n\n【简历优势】\n- 具体列出与JD匹配的亮点，每条用\"- \"开头，至少写3条，要结合简历中的具体内容\n- 每条优势都要有具体的技能/项目/经验支撑\n\n【简历不足与改进建议】\n- 具体列出与JD要求有明显差距的地方，每条用\"- \"开头，至少写3条\n- 针对每条不足给出可操作的改进建议"
    content = call_llm([{"role": "user", "content": prompt}], temperature=0.1)

    short_advantage = ""
    short_shortcoming = ""
    full_report = content

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
            short_shortcoming = parts[0].strip()[:100] if parts else ""

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
    prompt = "你是一个专业招聘顾问，根据候选人简历内容回答其问题。\n\n【简历内容】\n" + resume_text[:2000] + "\n\n【候选人问题】\n" + question + "\n\n请给出具体、有针对性、可操作的回答。如果简历中缺乏相关信息，也请诚实指出。"
    return call_llm([{"role": "user", "content": prompt}], temperature=0.5)


def generate_free_reply(history_list, user_input):
    """
    生成自由对话回复
    :param history_list: 对话历史列表
    :param user_input: 用户最新输入
    :return: AI 回复
    """
    recent = history_list[-6:] if len(history_list) > 6 else history_list
    history_text = "\n".join(
        [("用户: " + m['content']) if m['role'] == 'user' else ("助手: " + m['content']) for m in recent]
    )

    prompt = "你是一个专业的智聘未来招聘助手。根据对话历史，用自然、友好的语气回应用户，并尝试引导用户使用以下功能：\n- 查看在招岗位\n- 了解岗位具体要求\n- 上传简历\n- 评估简历与岗位的匹配度\n- 获取简历优化建议\n\n不要编造虚构信息。如果用户想了解岗位，提醒他们可以直接说出岗位名称。\n当前对话历史：\n" + history_text + "\n用户最新输入：" + user_input + "\n\n请直接给出助手回复："

    return call_llm([{"role": "user", "content": prompt}], temperature=0.7)
