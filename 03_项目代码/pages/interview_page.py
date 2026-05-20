import streamlit as st
import sys
import os
import json
import threading

# 设置 Python 路径以找到后端模块
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # pages/
project_root = os.path.dirname(current_file_dir)  # 03_项目代码/
sys.path.insert(0, project_root)

from interview_service import (
    verify_interview_token,
    update_interview_status,
    generate_questions_for_module,
    update_module_questions,
    score_interview
)
from utils import read_resume_text
from database import get_jd_from_db
from ai_scorer import call_llm

st.set_page_config(page_title="智聘未来 - AI面试", page_icon="🎤", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #fcfaf2; font-family: "Microsoft YaHei", sans-serif; }
    .interview-header { text-align: center; padding: 20px; }
    .question-card { background: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

token = st.query_params.get("token", None)
if not token:
    st.error("❌ 缺少面试链接参数，请从邮件中的链接进入。")
    st.stop()

is_valid, record, msg = verify_interview_token(token)
if not is_valid:
    st.error(f"❌ {msg}")
    st.stop()

st.markdown(f"""
<div class="interview-header">
    <h2>🎤 智聘未来 AI 智能面试</h2>
    <p>应聘岗位：{record['job_name']}</p>
    <p>面试链接有效期至：{record['expired_at'].strftime('%Y-%m-%d %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
    st.session_state.current_module = 0
    st.session_state.module_questions = []
    st.session_state.module_answers = []
    st.session_state.all_answers = []
    st.session_state.resume_text = ""
    st.session_state.jd_content = ""

if not st.session_state.resume_text and record.get('resume_id'):
    resume_path = f"../01_简历投递收件箱/{record['resume_id']}"
    if os.path.exists(resume_path):
        st.session_state.resume_text = read_resume_text(resume_path)
if not st.session_state.jd_content and record.get('job_name'):
    st.session_state.jd_content = get_jd_from_db(record['job_name'])

if not st.session_state.interview_started:
    st.markdown("""
    ### 📋 面试须知
    1. 本面试共包含**5个模块**：基础知识、项目经历、实习经历、技能实战、技能进阶实战
    2. 每个模块2-3题，总计约12题
    3. 请认真作答，提交后不可回退
    4. 面试结果将在48小时内通过邮件通知
    """)
    if st.button("✅ 开始面试", type="primary", use_container_width=True):
        st.session_state.interview_started = True
        update_interview_status(token, '进行中')
        st.rerun()
    st.stop()

MODULE_NAMES = ["基础知识", "项目经历", "实习经历", "技能实战", "技能进阶实战"]
current_idx = st.session_state.current_module

if current_idx < len(MODULE_NAMES):
    module_name = MODULE_NAMES[current_idx]

    if not st.session_state.module_questions:
        st.session_state.module_questions = generate_questions_for_module(
            module_name, st.session_state.resume_text, st.session_state.jd_content
        )
        update_module_questions(token, module_name, st.session_state.module_questions)
        st.session_state.module_answers = []

    st.markdown(f"### 📝 模块{current_idx+1}：{module_name}")
    st.markdown(f"*共{len(st.session_state.module_questions)}题*")

    answer_idx = len(st.session_state.module_answers)
    if answer_idx < len(st.session_state.module_questions):
        q = st.session_state.module_questions[answer_idx]
        st.markdown(f"""
        <div class="question-card">
            <strong>第{answer_idx+1}题：</strong><br>
            {q['question']}
        </div>
        """, unsafe_allow_html=True)
        user_answer = st.text_area("请输入您的回答：", height=150, key=f"ans_{current_idx}_{answer_idx}")
        if st.button("提交回答并进入下一题", key=f"sub_{current_idx}_{answer_idx}", use_container_width=True):
            if user_answer.strip():
                st.session_state.module_answers.append({
                    "module": module_name,
                    "question": q['question'],
                    "reference_answer": q.get('reference_answer', ''),
                    "scoring_points": q.get('scoring_points', []),
                    "answer": user_answer
                })
                st.rerun()
            else:
                st.warning("请填写您的回答后再提交。")
    else:
        st.success(f"✅ {module_name}模块已完成！")
        if st.button("进入下一模块", type="primary", use_container_width=True):
            st.session_state.all_answers.extend(st.session_state.module_answers)
            st.session_state.current_module += 1
            st.session_state.module_questions = []
            st.session_state.module_answers = []
            st.rerun()
else:
    st.markdown("### 🎉 面试完成！")
    st.markdown("感谢您的参与，面试结果将通过邮件通知。")
    if "submitted" not in st.session_state:
        if st.button("📤 提交面试结果", type="primary", use_container_width=True):
            update_interview_status(token, 'completed')
            threading.Thread(
                target=score_interview,
                args=(token, st.session_state.all_answers, record),
                daemon=True
            ).start()
            st.session_state.submitted = True
            st.rerun()
    else:
        st.success("您的面试答案已成功提交！")
