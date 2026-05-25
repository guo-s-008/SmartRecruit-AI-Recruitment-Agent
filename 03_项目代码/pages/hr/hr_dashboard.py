
import streamlit as st
import sys
import os

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from database import (
    query_jobs_from_db,
    get_all_talents,
    recommend_talents_for_job,
    add_talent_to_pool,
    get_all_jobs,
    update_job_status,
    delete_job,
    update_talent_status,
    search_talents
)
from log_system import write_hr_log

# 页面配置
st.set_page_config(page_title="HR管理后台", page_icon="🎯", layout="wide")

# 样式
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .section-header { font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# 侧边栏导航
st.sidebar.title("🎯 HR管理后台")
page = st.sidebar.radio("导航菜单", ["仪表盘", "岗位管理", "人才库", "简历管理", "面试管理"])

# 获取统计数据
def get_stats():
    talents = get_all_talents()
    jobs = query_jobs_from_db()
    return {
        "talent_count": len(talents),
        "job_count": len(jobs),
        "active_talents": len([t for t in talents if t['status'] == 'active'])
    }

stats = get_stats()

# 仪表盘页面
if page == "仪表盘":
    st.title("📊 HR管理仪表盘")
    
    # 统计卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("人才库总数", stats['talent_count'])
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("活跃人才", stats['active_talents'])
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("招聘岗位", stats['job_count'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 快速操作
    st.subheader("⚡ 快速操作")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("查看人才库", use_container_width=True):
            st.session_state.page = "人才库"
            st.rerun()
    with col2:
        if st.button("管理岗位", use_container_width=True):
            st.session_state.page = "岗位管理"
            st.rerun()
    
    # 岗位人才推荐
    st.subheader("🎯 岗位人才推荐")
    jobs = query_jobs_from_db()
    selected_job = st.selectbox("选择岗位", jobs)
    
    if selected_job:
        recommended = recommend_talents_for_job(selected_job, limit=3)
        if recommended:
            st.write(f"为「{selected_job}」推荐以下人才：")
            for talent in recommended:
                with st.expander(f"{talent['name']} - {talent['education']} - {talent['city']}"):
                    st.write(f"**技能**: {talent['skills']}")
                    st.write(f"**经验**: {talent['experience']}")
                    if st.button(f"邀请面试", key=f"invite_{talent['id']}"):
                        write_hr_log("update", "HR", f"邀请 {talent['name']} 面试 {selected_job}", "", f"已邀请")
                        st.success(f"已邀请 {talent['name']} 面试 {selected_job}")
        else:
            st.info("暂无匹配的人才推荐")

# 岗位管理页面
elif page == "岗位管理":
    st.title("🏢 岗位管理")
    
    # 添加岗位
    with st.expander("添加新岗位"):
        job_name = st.text_input("岗位名称")
        jd_content = st.text_area("岗位描述")
        education = st.selectbox("学历要求", ["不限", "本科", "硕士", "博士"])
        city = st.text_input("工作城市")
        hiring_count = st.number_input("招聘人数", min_value=1, value=1)
        if st.button("添加岗位"):
            write_hr_log("add", "HR", job_name, "", f"添加岗位")
            st.success(f"岗位「{job_name}」已添加")
    
    # 岗位列表
    st.subheader("岗位列表")
    jobs = query_jobs_from_db()
    for job in jobs:
        with st.expander(job):
            st.write("暂无详细信息")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("编辑", key=f"edit_{job}"):
                    st.write(f"编辑 {job}")
            with col2:
                if st.button("删除", key=f"del_{job}"):
                    write_hr_log("delete", "HR", job, "", "已删除")
                    st.success(f"岗位「{job}」已删除")

# 人才库页面
elif page == "人才库":
    st.title("💼 人才库管理")
    
    # 搜索
    keyword = st.text_input("搜索关键词")
    col1, col2 = st.columns(2)
    with col1:
        education = st.selectbox("学历筛选", ["全部", "本科", "硕士", "博士"])
    with col2:
        city = st.selectbox("城市筛选", ["全部", "北京", "上海", "深圳", "杭州"])
    
    # 人才列表
    talents = get_all_talents()
    if keyword:
        talents = [t for t in talents if keyword.lower() in t['name'].lower() or keyword.lower() in (t['skills'] or '')]
    if education != "全部":
        talents = [t for t in talents if t['education'] == education]
    if city != "全部":
        talents = [t for t in talents if t['city'] == city]
    
    for talent in talents:
        with st.expander(f"{talent['name']} - {talent['email']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**学历**: {talent['education']}")
                st.write(f"**城市**: {talent['city']}")
                st.write(f"**专业**: {talent['major']}")
            with col2:
                st.write(f"**技能**: {talent['skills']}")
                st.write(f"**状态**: {'✅ 活跃' if talent['status'] == 'active' else '❌ 已归档'}")
            
            if st.button(f"邀请面试", key=f"talent_invite_{talent['id']}"):
                write_hr_log("update", "HR", f"邀请 {talent['name']}", "", "已邀请面试")
                st.success(f"已邀请 {talent['name']}")

# 简历管理页面
elif page == "简历管理":
    st.title("📄 简历管理")
    st.info("简历管理功能开发中...")

# 面试管理页面
elif page == "面试管理":
    st.title("🎤 面试管理")
    st.info("面试管理功能开发中...")

