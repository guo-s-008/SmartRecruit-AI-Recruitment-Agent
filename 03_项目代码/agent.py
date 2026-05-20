
"""
agent.py - 兼容原有接口的模块（已废弃，保留用于兼容性）
所有功能已重构到 backend 模块中
"""
import os
import shutil
import pandas as pd
import time
from backend.config import UPLOAD_FOLDER, PROCESSED_FOLDER
from backend.utils import (
    read_resume_text,
    get_matched_jd_content,
    extract_email,
    extract_major,
    extract_education,
    extract_city,
    extract_target_city
)
from backend.ai_scorer import ai_score_resume_with_jd
from backend.email_service import (
    send_email,
    send_interview_result_email,
    send_interview_invitation_email
)
from backend.database import save_to_mysql
from backend.log_system import write_recruit_log

SELECTED_JOB_FROM_WEB = None

os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def process_new_files():
    """处理新投递的简历文件"""
    global SELECTED_JOB_FROM_WEB
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    except:
        return

    for file in files:
        fp = os.path.join(UPLOAD_FOLDER, file)
        print(f"\n========== 发现新简历：{file} ==========")

        resume_text = read_resume_text(fp)
        if not resume_text:
            shutil.move(fp, os.path.join(PROCESSED_FOLDER, file))
            continue

        email = extract_email(resume_text)
        print(f"📩 提取邮箱：{email}")

        job_title = file.split("_")[2]
        matched_jd_content = get_matched_jd_content(job_title)

        score, report = ai_score_resume_with_jd(resume_text, matched_jd_content, job_title)
        print(f"🎯 AI 打分：{score}")

        mail_status = "失败"
        if email:
            apply_result = "录用" if score >= 85 else "不合适"
            mail_status = send_email(email, score, job_title, apply_result, report)

        shutil.move(fp, os.path.join(PROCESSED_FOLDER, file))

        major = extract_major(resume_text)
        education = extract_education(resume_text)
        city = extract_city(resume_text)
        target_city = extract_target_city(resume_text)

        result_status = "录用" if score >= 85 else "不合适"

        try:
            write_recruit_log(
                resume_name=file,
                job_name=job_title,
                score=score,
                email=email if email else "无邮箱",
                mail_status=mail_status,
                result_status=result_status
            )
        except Exception as e:
            print(f"⚠️ 日志写入失败：{e}")

        detail_file = "../04_数据文件/recruitment_detail.xlsx"
        detail_data = {
            "投递时间": time.strftime("%Y-%m-%d %H:%M:%S"),
            "岗位": job_title,
            "匹配JD摘要": matched_jd_content[:50] + "...",
            "专业": major,
            "学历": education,
            "所在城市": city,
            "意向地区": target_city,
            "得分": score,
            "邮箱": email if email else "",
            "邮件状态": mail_status,
            "测评结果": result_status
        }

        try:
            if os.path.exists(detail_file):
                df_detail = pd.read_excel(detail_file)
            else:
                df_detail = pd.DataFrame(columns=detail_data.keys())

            df_detail = pd.concat([df_detail, pd.DataFrame([detail_data])], ignore_index=True)
            df_detail.to_excel(detail_file, index=False)
            print("✅ 详细报表已保存至 recruitment_detail.xlsx")
            save_to_mysql(detail_data)
        except Exception as e:
            print("❌ 详细报表保存失败：", e)

