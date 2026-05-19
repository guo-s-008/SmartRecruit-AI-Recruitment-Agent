
"""
agent.py - 兼容原有接口的模块
所有功能已重构到独立模块中，此文件保持对外接口不变
"""
import os
import shutil
import pandas as pd
import time
from config import UPLOAD_FOLDER, PROCESSED_FOLDER
from utils import (
    read_resume_text,
    get_matched_jd_content,
    extract_email,
    extract_major,
    extract_education,
    extract_city,
    extract_target_city
)
from ai_scorer import ai_score_resume_with_jd
from email_service import (
    send_email,
    send_interview_result_email,
    send_interview_invitation_email
)
from database import save_to_mysql
from log_system import write_recruit_log

# 全局变量：接收前端传递的选中岗位（供app.py赋值）
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

        # 从文件名提取岗位
        job_title = file.split("_")[2]
        matched_jd_content = get_matched_jd_content(job_title)

        # 执行AI评分，传入匹配到的JD内容
        score, report = ai_score_resume_with_jd(resume_text, matched_jd_content, job_title)
        print(f"🎯 AI 打分：{score}")

        mail_status = "失败"
        if email:
            apply_result = "录用" if score &gt;= 85 else "不合适"
            mail_status = send_email(email, score, job_title, apply_result, report)

        shutil.move(fp, os.path.join(PROCESSED_FOLDER, file))

        major = extract_major(resume_text)
        education = extract_education(resume_text)
        city = extract_city(resume_text)
        target_city = extract_target_city(resume_text)

        result_status = "录用" if score &gt;= 85 else "不合适"

        # 日志系统
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

        # 详细Excel报表
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


# # ---------------------- 主程序 ----------------------
# if __name__ == "__main__":
#     print("🤖 AI招聘Agent已启动 (前端指定岗位匹配JD)")
#     print("📌 监听文件夹：", UPLOAD_FOLDER)
#     print("📌 JD库路径：", "../04_数据文件/job_jd")
#     while True:
#         process_new_files()
#         time.sleep(10)

