import streamlit as st
import os
import random
import time
from datetime import datetime
import logging
import sys

# 设置 Python 路径以找到后端模块
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # pages/main/
project_root = os.path.dirname(os.path.dirname(current_file_dir))  # 03_项目代码/
sys.path.insert(0, project_root)

from log_system import write_dialog_log
from email_service import send_interview_invitation_email
from excel_service import handle_save_to_excel
from database import (
    query_jobs_from_db,
    get_jd_from_db,
    save_to_mysql,
    get_db_connection
)
from resume_parser import handle_upload_and_parse
from ai_scorer import (
    handle_score,
    ask_resume_question,
    generate_free_reply
)
from email_service import handle_send_email
from log_system import write_recruit_log
from interview_service import create_interview_link

BACKEND_READY = True

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("chat_main")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "对话招聘"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    welcome_msg = (
        "您好！欢迎来到智聘未来 AI 招聘助手 🤖\n\n"
        "我可以帮您：\n"
        "• 📋 查看在招岗位\n"
        "• 📄 了解简历投递须知\n"
        "• 🔍 查询具体岗位要求\n"
        "• 📊 评估简历与岗位匹配度\n"
        "• 💡 获取简历优化建议\n\n"
        "请问有什么可以帮您的？"
    )
    st.session_state.chat_messages.append({"role": "assistant", "content": welcome_msg})
    try:
        write_dialog_log("assistant", welcome_msg)
    except Exception as e:
        logger.error(f"初始欢迎消息日志记录失败: {e}")

if "current_advantage" not in st.session_state:
    st.session_state.current_advantage = None
if "current_shortcoming" not in st.session_state:
    st.session_state.current_shortcoming = None
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "current_job" not in st.session_state:
    st.session_state.current_job = None
if "current_score" not in st.session_state:
    st.session_state.current_score = None
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None
if "last_uploaded_filename" not in st.session_state:
    st.session_state.last_uploaded_filename = None
if "show_job_buttons" not in st.session_state:
    st.session_state.show_job_buttons = False

st.set_page_config(
    page_title="智聘未来 - AI对话招聘系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

TARGET_JOBS = [
    "AI大数据工程师", "AI算法工程师", "AI应用开发工程师", "大数据开发工程师",
    "大数据运维开发工程师", "数据分析师", "数据科学家", "推荐算法工程师"
]
random.seed(202507)
random.shuffle(TARGET_JOBS)
SHUFFLED_JOBS = TARGET_JOBS.copy()

st.markdown("""
    <style>
    .stApp {
        background-color: #fcfaf2;
        font-family: "Microsoft YaHei", sans-serif;
    }
    .nav-container {
        display: flex; align-items: center; justify-content: space-between;
        background-color: #3498db; padding: 14px 30px; border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 16px;
    }
    .nav-title {
        font-size: 24px; font-weight: bold; color: #000000 !important;
        margin: 0; padding: 0;
    }
    .stButton>button {
        background-color: rgba(255,255,255,0.95); color: #2c3e50; border: none;
        font-size: 15px; font-weight: 600; padding: 10px 20px; border-radius: 8px;
        transition: all 0.2s; width: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #ffffff; color: #3498db; transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .quick-btns {
        display: flex; gap: 12px; flex-wrap: wrap;
        margin: 8px 0 20px 0;
    }
    [data-testid="stChatMessage"] {
        border-radius: 12px !important;
        padding: 12px 18px !important;
        margin: 8px 0 !important;
    }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    [data-testid="stFileUploader"] label { display: none; }
    </style>
    """, unsafe_allow_html=True)

def add_message(role, content):
    st.session_state.chat_messages.append({"role": role, "content": content})
    try:
        write_dialog_log(role, content)
    except Exception as e:
        logger.error(f"日志记录失败: {e}")

def process_user_input(user_input, uploaded_file=None):
    response = ""

    if uploaded_file is not None:
        upload_dir = "../01_简历投递收件箱"
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"chat_{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        parsed = handle_upload_and_parse(uploaded_file.getbuffer(), uploaded_file.name)
        st.session_state.parsed_data = parsed
        st.session_state.uploaded_file_path = filepath

        response = (
            f"📄 简历已接收并解析完成！\n\n"
            f"• 专业：{parsed.get('major', '未知')}\n"
            f"• 学历：{parsed.get('education', '未知')}\n"
            f"• 邮箱：{parsed.get('email', '未提取')}\n\n"
            f"您可以点击下方按钮直接选择岗位，或告诉我您想应聘的岗位名称。"
        )
        st.session_state.show_job_buttons = True
        return response

    text = user_input.strip()

    target_job = None
    for job in TARGET_JOBS:
        if job in text:
            target_job = job
            break
    if not target_job and "last_shown_jobs" in st.session_state:
        jobs = st.session_state.last_shown_jobs
        for kw, idx in [("第一个",0),("第二个",1),("第三个",2),("第四个",3),
                        ("第五个",4),("第六个",5),("第七个",6),("第八个",7),("最后",-1)]:
            if kw in text:
                try: target_job = jobs[idx]
                except: pass
                break
        if not target_job and any(k in text for k in ["选择","感兴趣","想投"]):
            job_list = "\n".join([f"{i+1}. {j}" for i,j in enumerate(jobs)])
            return f"请告诉我具体岗位名称，比如「{jobs[0]}」或「第一个岗位」。\n\n当前在招：\n{job_list}"

    if target_job:
        jd = get_jd_from_db(target_job)
        st.session_state.current_job = target_job
        return f"📋 **{target_job}** 的岗位要求：\n\n{jd}\n\n如需评估匹配度，请先上传简历。"

    if any(k in text for k in ["须知","格式","怎么投递"]):
        return "📌 简历投递须知：\n\n• 支持格式：PDF、DOCX、TXT\n• 请包含联系方式、教育背景、技能特长\n• 自动解析并匹配岗位\n\n请上传简历或告诉我您想投递的岗位。"

    if any(k in text for k in ["岗位","招聘","在招","职位","有哪些"]):
        jobs = query_jobs_from_db()
        st.session_state.last_shown_jobs = jobs
        job_list = "\n".join([f"{i+1}. {j}" for i,j in enumerate(jobs)])
        st.session_state.show_job_buttons = True
        return f"我们目前在招的岗位有：\n\n{job_list}\n\n您可以直接点击下方按钮选择岗位。"

    if any(k in text for k in ["匹配","打分","评估","适配"]):
        if not st.session_state.parsed_data:
            return "请先上传您的简历。"
        if not st.session_state.current_job:
            for job in TARGET_JOBS:
                if job in text:
                    st.session_state.current_job = job
                    break
        if not st.session_state.current_job:
            return "请指定要评估的岗位，例如「评估数据分析师匹配度」。"

        resume_text = st.session_state.parsed_data.get("text","")
        jd = get_jd_from_db(st.session_state.current_job)
        result = handle_score(st.session_state.current_job, resume_text, jd)
        st.session_state.current_score = result["score"]
        st.session_state.current_report = result["report"]
        st.session_state.current_advantage = result.get("advantage","")
        st.session_state.current_shortcoming = result.get("shortcoming","")

        return (
            f"📊 您与 **{st.session_state.current_job}** 的匹配度为 **{result['score']} 分**\n\n"
            f"{result['report']}\n\n"
            f"**✨ 简历亮点**\n{result.get('advantage','无')}\n\n"
            f"**⚠️ 待提升方向**\n{result.get('shortcoming','无')}\n\n"
            f"您可以继续问：\n• 「我的简历有什么不足？」\n• 「怎么优化简历？」\n• 「发送邮件回执」"
        )

    if any(k in text for k in ["不足","缺点","短板","优化","改进","建议"]):
        if not st.session_state.parsed_data or not st.session_state.current_report:
            return "请先完成岗位匹配评估。"
        resume_text = st.session_state.parsed_data.get("text","")
        return ask_resume_question(resume_text, "请基于我的简历和上次评估报告，详细分析不足并给出优化建议。")

    if any(k in text for k in ["投递","发送","邮件","回执"]):
        if not st.session_state.current_score or not st.session_state.parsed_data:
            return "请先完成岗位匹配评估。"
        email = st.session_state.parsed_data.get("email")
        if not email:
            return "简历中未提取到邮箱，无法发送。"
        job = st.session_state.current_job or "未知岗位"
        score = st.session_state.current_score
        report = st.session_state.current_report
        advantage = st.session_state.current_advantage or ""
        shortcoming = st.session_state.current_shortcoming or ""

        try:
            score_int = int(score)
        except:
            score_int = 0
        apply_result = "录用" if score_int >= 85 else "不合适"

        mail_status = handle_send_email(
            email, score, job, apply_result,
            report=report, advantage=advantage, shortcoming=shortcoming
        )

        if mail_status == "成功":
            parsed = st.session_state.parsed_data or {}
            detail_data = {
                "投递时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "姓名": parsed.get("name", ""),
                "性别": parsed.get("gender", ""),
                "年龄": parsed.get("age", ""),
                "学历": parsed.get("education", ""),
                "岗位": job,
                "专业": parsed.get("major", ""),
                "所在城市": parsed.get("city", ""),
                "意向地区": parsed.get("target_city", ""),
                "得分": score_int,
                "邮箱": email,
                "邮件状态": mail_status,
                "测评结果": apply_result
            }

            inserted_id = save_to_mysql(detail_data)

            detail_data["ID"] = inserted_id

            handle_save_to_excel(detail_data)

            write_recruit_log(
                resume_name=os.path.basename(st.session_state.uploaded_file_path or ""),
                job_name=job, score=score_int, email=email,
                mail_status=mail_status, result_status=apply_result
            )

            if apply_result == "录用":
                interview_url = create_interview_link(
                    email,
                    os.path.basename(st.session_state.uploaded_file_path or ""),
                    job,
                    inserted_id
                )
                if interview_url:
                    candidate_name = parsed.get("name", "")
                    if not candidate_name:
                        candidate_name = email.split("@")[0] if email else "同学"
                    send_interview_invitation_email(email, candidate_name, interview_url)

                    try:
                        conn = get_db_connection()
                        with conn.cursor() as cur:
                            token = interview_url.split("token=")[-1]
                            cur.execute(
                                "UPDATE resume_record SET interview_token=%s, interview_link=%s, interview_status='已发送' WHERE email=%s AND job=%s",
                                (token, interview_url, email, job)
                            )
                        conn.commit()
                        conn.close()
                        response = "✅ 评估报告已发送。\n\n📩 面试邀请邮件也已发出，请在48小时内完成AI初面。"
                    except Exception as e:
                        print(f"更新面试链接失败: {e}")
                        response = "✅ 评估报告已发送至您的邮箱，请注意查收。"
                else:
                    response = "✅ 评估报告已发送至您的邮箱，请注意查收。"
            else:
                response = "✅ 评估报告已发送至您的邮箱。根据本次评估结果，暂未达到面试标准，可优化简历后再次投递。"

            return response

def render_navbar():
    st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
    st.markdown('<h1 class="nav-title">🤖 智聘未来 - AI对话招聘系统</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("🤖 对话招聘", key="btn_chat", use_container_width=True):
            st.session_state.active_tab = "对话招聘"
    with col2:
        if st.button("📊 数据看板", key="btn_dashboard", use_container_width=True):
            st.session_state.active_tab = "数据看板"
    with col3:
        if st.button("❓ 使用帮助", key="btn_help", use_container_width=True):
            st.session_state.active_tab = "使用帮助"
    st.markdown("</div>", unsafe_allow_html=True)

def render_chat_page():
    st.markdown("<div class='quick-btns'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    quick_map = {
        c1: "📋 查看在招岗位",
        c2: "📄 简历投递须知",
        c3: "🔍 查询岗位要求",
        c4: "📊 评估简历匹配度"
    }
    for col, label in quick_map.items():
        with col:
            if st.button(label, key=f"q_{label}", use_container_width=True):
                add_message("user", label)
                resp = process_user_input(label)
                add_message("assistant", resp)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.get("show_job_buttons") and "last_shown_jobs" in st.session_state:
        st.markdown("**👇 快速选择岗位**")
        jobs = st.session_state.last_shown_jobs
        for i in range(0, len(jobs), 4):
            cols = st.columns(4)
            for j in range(4):
                idx = i + j
                if idx < len(jobs):
                    with cols[j]:
                        if st.button(f"📌 {jobs[idx]}", key=f"job_sel_{idx}", use_container_width=True):
                            st.session_state.show_job_buttons = False
                            add_message("user", f"我选择 {jobs[idx]} 岗位")
                            resp = process_user_input(f"我选择 {jobs[idx]} 岗位")
                            add_message("assistant", resp)
                            st.rerun()
        if st.button("关闭岗位列表"):
            st.session_state.show_job_buttons = False
            st.rerun()

    if st.session_state.current_report is not None and st.session_state.current_score is not None:
        st.markdown("**💡 您可以继续问：**")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔍 我的简历有什么不足？", key="btn_weakness", use_container_width=True):
                add_message("user", "我的简历有什么不足？")
                resp = process_user_input("我的简历有什么不足？")
                add_message("assistant", resp)
                st.rerun()
        with c2:
            if st.button("💡 怎么优化简历？", key="btn_improve", use_container_width=True):
                add_message("user", "怎么优化简历？")
                resp = process_user_input("怎么优化简历？")
                add_message("assistant", resp)
                st.rerun()
        with c3:
            if st.button("📧 发送邮件回执", key="btn_sendmail", use_container_width=True):
                add_message("user", "发送邮件回执")
                resp = process_user_input("发送邮件回执")
                add_message("assistant", resp)
                st.rerun()

    st.markdown("**📌 常用操作：**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📋 查看岗位", key="fixed_jobs", use_container_width=True):
            add_message("user", "查看在招岗位")
            resp = process_user_input("查看在招岗位")
            add_message("assistant", resp)
            st.rerun()
    with c2:
        if st.button("📄 投递须知", key="fixed_notice", use_container_width=True):
            add_message("user", "简历投递须知")
            resp = process_user_input("简历投递须知")
            add_message("assistant", resp)
            st.rerun()
    with c3:
        if st.button("🔍 岗位要求", key="fixed_req", use_container_width=True):
            add_message("user", "查询岗位要求")
            resp = process_user_input("查询岗位要求")
            add_message("assistant", resp)
            st.rerun()
    with c4:
        if st.button("📊 评估匹配", key="fixed_match", use_container_width=True):
            add_message("user", "评估简历匹配度")
            resp = process_user_input("评估简历匹配度")
            add_message("assistant", resp)
            st.rerun()

    col_input, col_upload = st.columns([5,1])
    with col_input:
        user_input = st.chat_input("请输入您的问题...")
    with col_upload:
        uploaded_file = st.file_uploader("📎", type=["pdf","docx","txt"], key="chat_uploader")

    if user_input:
        add_message("user", user_input)
        resp = process_user_input(user_input)
        add_message("assistant", resp)
        st.rerun()

    if uploaded_file and uploaded_file.name != st.session_state.last_uploaded_filename:
        st.session_state.last_uploaded_filename = uploaded_file.name
        add_message("user", f"📎 上传了简历：{uploaded_file.name}")
        resp = process_user_input("", uploaded_file)
        add_message("assistant", resp)
        st.rerun()

def render_dashboard():
    st.title("📊 数据看板")
    st.info("数据看板模块开发中，将展示招聘数据统计。")

def render_help():
    st.title("❓ 使用帮助")
    st.markdown("""
    **使用流程：**
    1. 上传简历（PDF/DOCX/TXT）
    2. 查询岗位要求
    3. 评估匹配度
    4. 获取优化建议
    5. 发送邮件回执
    """)

render_navbar()
if st.session_state.active_tab == "对话招聘":
    render_chat_page()
elif st.session_state.active_tab == "数据看板":
    render_dashboard()
elif st.session_state.active_tab == "使用帮助":
    render_help()
