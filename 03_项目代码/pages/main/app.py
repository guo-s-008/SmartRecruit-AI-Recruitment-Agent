import streamlit as st
import os
import random
from datetime import datetime
import sys

# 设置 Python 路径以找到后端模块
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # pages/main/
project_root = os.path.dirname(os.path.dirname(current_file_dir))  # 03_项目代码/
sys.path.insert(0, project_root)

from config import UPLOAD_FOLDER

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "校园招聘"

st.set_page_config(
    page_title="智聘未来 - AI智能招聘系统",
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
    .stApp { background-color: #f8f9fa; font-family: "Microsoft YaHei", sans-serif; }
    .nav-container {
        display: flex; align-items: center; justify-content: space-between;
        background-color: #3498db; padding: 14px 30px; border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 24px;
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
    .form-section { margin-bottom: 20px; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
st.markdown('<h1 class="nav-title">智聘未来 - AI智能招聘系统</h1>', unsafe_allow_html=True)

col1, col3, col4 = st.columns([1, 1, 1])
with col1:
    if st.button("校园招聘", key="btn_campus"): st.session_state.active_tab = "校园招聘"
with col3:
    if st.button("招聘FAQ", key="btn_faq"): st.session_state.active_tab = "招聘FAQ"
with col4:
    if st.button("关于工作", key="btn_about"): st.session_state.active_tab = "关于工作"

st.markdown("</div>", unsafe_allow_html=True)


def show_campus_page():
    st.title("🎓 校园招聘投递")
    st.divider()

    st.header("📌 实习岗投递")
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("🔍 选择目标实习岗位")
    selected_intern_job = st.selectbox("", options=SHUFFLED_JOBS, index=0, key="intern_job_sel")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("📄 上传个人简历")
    uploaded_intern_file = st.file_uploader("", type=["pdf", "docx", "txt"], key="intern_file_up")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("📧 填写邮箱地址")
    intern_email = st.text_input("", placeholder="请输入你的邮箱地址", key="intern_email_txt")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("📱 填写手机号码")
    intern_phone = st.text_input("", placeholder="请输入你的手机号码", key="intern_phone_txt")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.header("💼 校园正式岗投递")
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader(" 选择目标正式岗位")
    selected_campus_job = st.selectbox("", options=SHUFFLED_JOBS, index=0, key="campus_job_sel")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("📄 上传个人简历")
    uploaded_campus_file = st.file_uploader("", type=["pdf", "docx", "txt"], key="campus_file_up")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("📧 填写邮箱地址")
    campus_email = st.text_input("", placeholder="请输入你的邮箱地址", key="campus_email_txt")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    st.subheader("📱 填写手机号码")
    campus_phone = st.text_input("", placeholder="请输入你的手机号码", key="campus_phone_txt")
    st.markdown("</div>", unsafe_allow_html=True)

    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        submit_btn = st.button(" 确认投递", type="primary", key="campus_submit", use_container_width=True)

    if submit_btn:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        if uploaded_intern_file is not None:
            if not intern_email or "@" not in intern_email:
                st.error("⚠️ 请填写有效的实习岗邮箱地址！")
            elif not intern_phone or len(intern_phone) != 11:
                st.error("⚠️ 请填写有效的实习岗手机号！")
            else:
                file_name = f"intern_{timestamp}_{selected_intern_job}_{uploaded_intern_file.name}"
                save_path = os.path.join(UPLOAD_FOLDER, file_name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_intern_file.getbuffer())
                st.success(f"✅ 实习岗投递成功！\n 岗位：{selected_intern_job} |  邮箱：{intern_email}")

        elif uploaded_campus_file is not None:
            if not campus_email or "@" not in campus_email:
                st.error("⚠️ 请填写有效的正式岗邮箱地址！")
            elif not campus_phone or len(campus_phone) != 11:
                st.error("⚠️ 请填写有效的正式岗手机号！")
            else:
                file_name = f"campus_{timestamp}_{selected_campus_job}_{uploaded_campus_file.name}"
                save_path = os.path.join(UPLOAD_FOLDER, file_name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_campus_file.getbuffer())
                st.success(f"✅ 正式岗投递成功！\n🎯 岗位：{selected_campus_job} | 📧 邮箱：{campus_email}")
        else:
            st.error("⚠️ 请先上传对应岗位的简历文件！")


def show_faq_page():
    st.title("❓ 招聘FAQ")
    st.info("常见问题解答模块正在完善中，敬请期待...")


def show_about_page():
    st.title("📌 关于工作")
    st.info("企业文化与福利介绍模块正在完善中，敬请期待...")


page_mapping = {
    "校园招聘": show_campus_page,
    "招聘FAQ": show_faq_page,
    "关于工作": show_about_page
}

if st.session_state.active_tab in page_mapping:
    page_mapping[st.session_state.active_tab]()
