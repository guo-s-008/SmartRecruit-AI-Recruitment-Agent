
"""
agent_service.py - 后端服务层（兼容原有接口，已废弃）
所有功能已重构到 backend 模块中
前端代码应直接从 backend 导入
"""
from backend.config import APP_BASE_URL, INTERVIEW_CONFIG
from backend.database import (
    get_db_connection,
    query_jobs_from_db,
    get_jd_from_db,
    get_scoring_criteria_from_db,
    save_to_mysql as _save_to_mysql
)
from backend.resume_parser import handle_upload_and_parse
from backend.ai_scorer import (
    call_llm,
    handle_score,
    ask_resume_question,
    generate_free_reply
)
from backend.utils import summarize_text
from backend.email_service import (
    send_email as _send_email,
    send_interview_result_email,
    send_interview_invitation_email,
    handle_send_email
)
from backend.excel_service import (
    handle_save_to_excel,
    update_excel_interview_scores
)
from backend.interview_service import (
    create_interview_link,
    verify_interview_token,
    update_interview_status,
    generate_questions_for_module,
    update_module_questions,
    score_interview
)
from backend.log_system import write_recruit_log


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


def handle_save_to_db(detail_data):
    """将简历评分结果写入 MySQL（resume_record 表）"""
    return _save_to_mysql(detail_data)


def handle_log(resume_name, job_name, score, email, mail_status, result_status):
    """将投递、评分结果写入 log_dayinfo 日志文件"""
    write_recruit_log(
        resume_name=resume_name,
        job_name=job_name,
        score=score,
        email=email,
        mail_status=mail_status,
        result_status=result_status
    )


def read_resume_text_from_file(filepath):
    """读取简历文本，供面试页调用（兼容旧函数名）"""
    from backend.utils import read_resume_text
    return read_resume_text(filepath)


def send_interview_emails(email, job_name, scores, total, apply_result, all_answers):
    """面试结果双端邮件（兼容旧函数名）"""
    send_interview_result_email(email, job_name, scores, total, apply_result, all_answers)


def send_invitation_email(email, candidate_name, interview_url):
    """调用 agent.py 发送面试邀请邮件（兼容旧函数名）"""
    return send_interview_invitation_email(email, candidate_name, interview_url)

