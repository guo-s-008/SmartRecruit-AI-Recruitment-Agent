
"""
多候选人对比页面
"""
import streamlit as st
import sys
import os

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from database import get_all_talents, search_talents
from log_system import write_hr_log
from ai_scorer import analyze_candidates_comparison

# 页面配置
st.set_page_config(page_title="候选人对比", page_icon="⚖️", layout="wide")

st.title("⚖️ 多候选人对比")

# 获取候选人列表
talents = get_all_talents()

if len(talents) < 2:
    st.warning("人才库中至少需要2个候选人才可以进行对比")
    st.stop()

# 选择要对比的候选人
st.subheader("选择要对比的候选人")
selected_talents = st.multiselect(
    "选择候选人（最多选择5个）",
    options=[f"{t['name']} - {t['education']} - {t['city']}" for t in talents],
    default=[],
    max_selections=5
)

if len(selected_talents) < 2:
    st.info("请选择至少2个候选人进行对比")
    st.stop()

# 提取选中的候选人对象
selected_talent_objects = []
for name in selected_talents:
    for t in talents:
        if f"{t['name']} - {t['education']} - {t['city']}" == name:
            selected_talent_objects.append(t)
            break

# 显示对比表格
st.subheader("候选人对比分析")

# 创建对比数据
comparison_data = []
for talent in selected_talent_objects:
    comparison_data.append({
        "姓名": talent['name'],
        "性别": talent['gender'],
        "年龄": talent['age'],
        "学历": talent['education'],
        "专业": talent['major'],
        "城市": talent['city'],
        "技能": talent['skills'],
        "经验": talent['experience']
    })

# 显示对比表格
import pandas as pd
df = pd.DataFrame(comparison_data)
st.dataframe(df, use_container_width=True)

# AI分析比对点
st.subheader("🤖 AI智能分析比对")

# 比对维度
st.write("**比对维度：**")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("📚 学历背景")
with col2:
    st.write("💼 技能匹配")
with col3:
    st.write("🏢 经验相关")

# 分析按钮
if st.button("🔍 AI分析比对点", type="primary"):
    write_hr_log("query", "HR", "多候选人对比分析", "", f"对比候选人: {', '.join([t['name'] for t in selected_talent_objects])}")
    
    with st.spinner("🤖 AI正在分析中，请稍候..."):
        try:
            # 调用真实的AI分析
            ai_analysis = analyze_candidates_comparison(selected_talent_objects)
            
            if "⚠️" in ai_analysis or "错误" in ai_analysis or "失败" in ai_analysis:
                st.error(ai_analysis)
                st.info("💡 提示：请确保已在【04_数据文件/.env】中配置了有效的 API_KEY")
                
                # 提供基础统计作为备选方案
                st.subheader("📊 基础统计分析（备选方案）")
                show_basic_stats(selected_talent_objects)
            else:
                st.success("✅ AI分析完成！")
                
                # 美化显示AI分析结果
                display_ai_analysis(ai_analysis)
                
        except Exception as e:
            st.error(f"AI分析出错：{str(e)}")
            import traceback
            traceback.print_exc()
            st.info("💡 提供基础统计分析：")
            show_basic_stats(selected_talent_objects)


def show_basic_stats(candidates):
    """显示基础统计分析"""
    # 学历对比
    st.write("\n**📚 学历背景分析：**")
    education_scores = {}
    for talent in candidates:
        edu = talent['education']
        if edu not in education_scores:
            education_scores[edu] = 0
        education_scores[edu] += 1
    
    for edu, count in sorted(education_scores.items(), key=lambda x: x[1], reverse=True):
        st.write(f"  • {edu}: {count}人")

    # 技能对比
    st.write("\n**💼 技能匹配分析：**")
    all_skills = {}
    for talent in candidates:
        skills = talent['skills'].split(',') if talent['skills'] else []
        for skill in skills:
            skill = skill.strip()
            if skill:
                if skill not in all_skills:
                    all_skills[skill] = 0
                all_skills[skill] += 1
    
    top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
    st.write("**热门技能：**")
    for skill, count in top_skills:
        st.write(f"  • {skill}: {count}人")

    # 城市分布
    st.write("\n**🏙️ 城市分布分析：**")
    city_scores = {}
    for talent in candidates:
        city = talent['city']
        if city not in city_scores:
            city_scores[city] = 0
        city_scores[city] += 1
    
    for city, count in sorted(city_scores.items(), key=lambda x: x[1], reverse=True):
        st.write(f"  • {city}: {count}人")


def display_ai_analysis(analysis_text):
    """美化显示AI分析结果"""
    # 使用Markdown格式显示
    st.markdown("---")
    
    # 分段显示分析结果
    sections = analysis_text.split("【")
    
    for section in sections[1:]:  # 跳过第一个空字符串
        if "】" in section:
            title, content = section.split("】", 1)
            st.subheader(f"【{title.strip()}】")
            st.write(content.strip())
            st.markdown("---")

# HR抽查功能
st.subheader("🎯 HR抽查")
st.write("从选中的候选人中随机抽查：")

if st.button("🎲 随机抽查1人"):
    import random
    selected = random.choice(selected_talent_objects)
    st.success(f"✅ 抽查结果：{selected['name']}")
    st.write(f"**姓名**: {selected['name']}")
    st.write(f"**学历**: {selected['education']}")
    st.write(f"**专业**: {selected['major']}")
    st.write(f"**城市**: {selected['city']}")
    st.write(f"**技能**: {selected['skills']}")
    st.write(f"**经验**: {selected['experience']}")
    
    write_hr_log("update", "HR", f"抽查候选人: {selected['name']}", "", "已抽查")

# 批量操作
st.subheader("⚡ 批量操作")
st.write("对选中的候选人执行批量操作：")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📧 批量发送面试邀请"):
        names = [t['name'] for t in selected_talent_objects]
        write_hr_log("update", "HR", "批量面试邀请", "", f"候选人: {', '.join(names)}")
        st.success(f"✅ 已向 {len(selected_talent_objects)} 人发送面试邀请")

with col2:
    if st.button("📁 批量标记为待定"):
        names = [t['name'] for t in selected_talent_objects]
        write_hr_log("update", "HR", "批量标记待定", "", f"候选人: {', '.join(names)}")
        st.success(f"✅ 已标记 {len(selected_talent_objects)} 人为待定")

with col3:
    if st.button("🗑️ 批量归档"):
        names = [t['name'] for t in selected_talent_objects]
        write_hr_log("delete", "HR", "批量归档", "", f"候选人: {', '.join(names)}")
        st.success(f"✅ 已归档 {len(selected_talent_objects)} 人")

# 查看详情
st.subheader("📋 候选人详情")
for i, talent in enumerate(selected_talent_objects):
    with st.expander(f"{talent['name']} - 详情"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**姓名**: {talent['name']}")
            st.write(f"**性别**: {talent['gender']}")
            st.write(f"**年龄**: {talent['age']}")
            st.write(f"**学历**: {talent['education']}")
        with col2:
            st.write(f"**专业**: {talent['major']}")
            st.write(f"**城市**: {talent['city']}")
            st.write(f"**状态**: {'✅ 活跃' if talent['status'] == 'active' else '❌ 已归档'}")
        
        st.write(f"**技能**: {talent['skills']}")
        st.write(f"**经验**: {talent['experience']}")
        st.write(f"**标签**: {talent['tags']}")
        st.write(f"**来源**: {talent['source']}")
        
        if st.button(f"查看简历", key=f"view_{i}"):
            st.text(talent['resume_text'])

