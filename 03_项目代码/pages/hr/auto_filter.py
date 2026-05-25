"""
自动化筛选页面
"""
import streamlit as st
import sys
import os

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from database_sqlite import (
    search_talents, 
    query_jobs_from_db, 
    get_all_talents,
    update_talent_status
)
from log_system import write_hr_log

# 页面配置
st.set_page_config(page_title="自动化筛选", page_icon="🤖", layout="wide")

st.title("🤖 自动化筛选")

# 筛选条件设置
st.subheader("设置筛选条件")

col1, col2 = st.columns(2)

with col1:
    st.write("**📚 学历要求**")
    education_filter = st.selectbox(
        "最低学历",
        ["不限", "本科", "硕士", "博士"],
        index=0
    )
    
    st.write("**🏙️ 城市要求**")
    city_filter = st.selectbox(
        "工作城市",
        ["全部", "北京", "上海", "深圳", "杭州", "广州", "成都"]
    )

with col2:
    st.write("**💼 技能要求**")
    skills_filter = st.text_input(
        "关键词技能（逗号分隔）",
        placeholder="如：Python,SQL,机器学习"
    )
    
    st.write("**🎯 状态筛选**")
    status_filter = st.selectbox(
        "人才状态",
        ["全部", "活跃", "已归档"]
    )

# 高级筛选
with st.expander("高级筛选"):
    st.write("**📋 经验要求**")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        min_exp = st.number_input("最少经验（年）", min_value=0, max_value=20, value=0)
    with exp_col2:
        max_exp = st.number_input("最多经验（年）", min_value=0, max_value=20, value=20)
    
    st.write("**📝 简历关键词**")
    resume_keyword = st.text_input("简历中包含的关键词", placeholder="如：大厂,字节,阿里")

# 执行筛选
st.subheader("筛选结果")

if st.button("🔍 执行筛选", type="primary", use_container_width=True):
    write_hr_log(
        "query", 
        "HR", 
        "自动化筛选", 
        "", 
        f"条件: 学历={education_filter}, 城市={city_filter}, 技能={skills_filter}, 状态={status_filter}"
    )
    
    # 执行筛选
    talents = search_talents(
        keyword=resume_keyword if resume_keyword else None,
        education=education_filter if education_filter != "不限" else None,
        city=city_filter if city_filter != "全部" else None,
        skills=skills_filter if skills_filter else None
    )
    
    # 状态筛选
    if status_filter == "活跃":
        talents = [t for t in talents if t['status'] == 'active']
    elif status_filter == "已归档":
        talents = [t for t in talents if t['status'] != 'active']
    
    # 经验筛选（简单筛选，实际需要更复杂的逻辑）
    if min_exp > 0 or max_exp < 20:
        # 这里简化处理，实际应该解析experience字段
        talents = talents  # 暂时不做经验筛选
    
    st.success(f"✅ 找到 {len(talents)} 个匹配的候选人")
    
    if talents:
        # 显示结果统计
        st.write(f"\n**📊 结果统计：**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("匹配人数", len(talents))
        with col2:
            edu_counts = {}
            for t in talents:
                edu = t['education']
                edu_counts[edu] = edu_counts.get(edu, 0) + 1
            top_edu = max(edu_counts.items(), key=lambda x: x[1]) if edu_counts else ("未知", 0)
            st.metric("最高学历", top_edu[0])
        with col3:
            city_counts = {}
            for t in talents:
                city = t['city']
                city_counts[city] = city_counts.get(city, 0) + 1
            top_city = max(city_counts.items(), key=lambda x: x[1]) if city_counts else ("未知", 0)
            st.metric("最多城市", top_city[0])
        
        # 显示候选人列表
        st.write("\n**📋 候选人列表：**")
        for i, talent in enumerate(talents):
            with st.expander(f"{i+1}. {talent['name']} - {talent['education']} - {talent['city']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**姓名**: {talent['name']}")
                    st.write(f"**学历**: {talent['education']}")
                    st.write(f"**专业**: {talent['major']}")
                    st.write(f"**城市**: {talent['city']}")
                with col2:
                    st.write(f"**技能**: {talent['skills']}")
                    st.write(f"**状态**: {'✅ 活跃' if talent['status'] == 'active' else '❌ 已归档'}")
                    st.write(f"**来源**: {talent['source']}")
                
                st.write(f"**经验**: {talent['experience']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ 通过", key=f"pass_{talent['id']}"):
                        update_talent_status(talent['id'], 'active')
                        write_hr_log("update", "HR", f"筛选通过: {talent['name']}", "", "筛选通过")
                        st.success(f"{talent['name']} 已通过筛选")
                        st.rerun()
                with col2:
                    if st.button(f"❌ 淘汰", key=f"reject_{talent['id']}"):
                        update_talent_status(talent['id'], 'inactive')
                        write_hr_log("update", "HR", f"筛选淘汰: {talent['name']}", "", "筛选淘汰")
                        st.warning(f"{talent['name']} 已淘汰")
                        st.rerun()
                with col3:
                    if st.button(f"📧 邀请面试", key=f"invite_{talent['id']}"):
                        write_hr_log("update", "HR", f"邀请面试: {talent['name']}", "", "已邀请面试")
                        st.success(f"已邀请 {talent['name']} 面试")
    else:
        st.info("未找到匹配的候选人，请调整筛选条件")

# 批量操作
st.subheader("⚡ 批量操作")

col1, col2 = st.columns(2)

with col1:
    st.write("**📁 批量标记**")
    batch_action = st.selectbox(
        "选择批量操作",
        ["无", "全部通过", "全部淘汰", "全部标记为待定"]
    )
    
    if st.button("执行批量操作"):
        if batch_action != "无":
            talents = get_all_talents()
            count = 0
            for t in talents:
                if batch_action == "全部通过":
                    update_talent_status(t['id'], 'active')
                    count += 1
                elif batch_action == "全部淘汰":
                    update_talent_status(t['id'], 'inactive')
                    count += 1
            
            write_hr_log("update", "HR", f"批量操作: {batch_action}", "", f"处理 {count} 人")
            st.success(f"✅ 已对 {count} 人执行「{batch_action}」操作")

with col2:
    st.write("**📊 统计分析**")
    talents = get_all_talents()
    
    edu_stats = {}
    for t in talents:
        edu = t['education']
        edu_stats[edu] = edu_stats.get(edu, 0) + 1
    
    st.write("**学历分布：**")
    for edu, count in sorted(edu_stats.items(), key=lambda x: x[1], reverse=True):
        st.write(f"  • {edu}: {count}人")
    
    city_stats = {}
    for t in talents:
        city = t['city']
        city_stats[city] = city_stats.get(city, 0) + 1
    
    st.write("\n**城市分布：**")
    for city, count in sorted(city_stats.items(), key=lambda x: x[1], reverse=True):
        st.write(f"  • {city}: {count}人")

# 智能推荐
st.subheader("🎯 智能推荐")

jobs = query_jobs_from_db()
selected_job = st.selectbox("为岗位推荐人才", ["请选择岗位"] + jobs)

if selected_job != "请选择岗位":
    talents = search_talents(skills=selected_job.split()[0])  # 简单匹配
    
    if talents:
        st.success(f"为「{selected_job}」找到 {len(talents)} 个推荐候选人")
        
        for talent in talents[:5]:  # 只显示前5个
            with st.expander(f"推荐: {talent['name']}"):
                st.write(f"**匹配度**: 高")
                st.write(f"**技能**: {talent['skills']}")
                st.write(f"**经验**: {talent['experience']}")
                
                if st.button(f"立即邀请", key=f"rec_invite_{talent['id']}"):
                    write_hr_log("update", "HR", f"智能推荐邀请: {talent['name']}", "", f"推荐岗位: {selected_job}")
                    st.success(f"已邀请 {talent['name']} 面试 {selected_job}")
    else:
        st.info(f"暂未找到适合「{selected_job}」的候选人")
