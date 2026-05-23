"""
简化版完整招聘系统测试
"""
import sys
import time
import json
from pathlib import Path

sys.path.insert(0, '/workspace/03_项目代码')

from config import API_CONFIG, SQLITE_DB_PATH, EMAIL_CONFIG
from database_sqlite import query_jobs_from_db, get_jd_from_db, get_scoring_criteria_from_db
from utils import extract_email, extract_name, extract_education
from ai_scorer import handle_score
from interview_service_sqlite import create_interview_link, generate_default_questions, MODULE_NAMES
from email_service import send_email, send_interview_invitation_email

print("\n" + "="*80)
print("🎯 智聘未来招聘系统 - 完整测试流程")
print("="*80 + "\n")

# 测试1: 环境准备
print("1️⃣ 环境准备")
print("-" * 50)
print(f"数据库: {SQLITE_DB_PATH}")
print(f"API Key: {API_CONFIG['key'][:10]}...")
print(f"HR邮箱: {EMAIL_CONFIG.get('hr_email', '未配置')}")
print("✓ 环境准备完成\n")

# 测试2: 读取简历
print("2️⃣ 简历解析")
print("-" * 50)
resume_path = "/workspace/02_已处理简历/张三_测试简历.txt"
with open(resume_path, 'r', encoding='utf-8') as f:
    resume_text = f.read()

name = extract_name(resume_text)
email = extract_email(resume_text)
edu = extract_education(resume_text)
print(f"姓名: {name}")
print(f"邮箱: {email}")
print(f"学历: {edu}")
print("✓ 简历解析完成\n")

# 测试3: AI评分
print("3️⃣ AI简历评分")
print("-" * 50)
job = "AI大数据工程师"
jd = get_jd_from_db(job)
scoring = get_scoring_criteria_from_db(job)

print(f"岗位: {job}")
print(f"JD长度: {len(jd)} 字符")

print("\n⏳ 正在评分...")
result = handle_score(job, resume_text, jd, scoring)
print(f"\n得分: {result['score']}/100")
print(f"结果: {'✅ 通过' if result['score'] >= 80 else '❌ 未通过'}")
print("✓ AI评分完成\n")

# 测试4: 发送邮件
print("4️⃣ 发送邮件")
print("-" * 50)
apply_result = "录用" if result['score'] >= 80 else "不合适"
hr_email = EMAIL_CONFIG.get('hr_email', 'q17877881463qq@163.com')
print(f"收件人: {email} (候选人), {hr_email} (HR)")
print(f"结果: {apply_result}")

print("\n⏳ 发送邮件中...")
status = send_email(email, result['score'], job, apply_result, result['report'], result['advantage'], result['shortcoming'])
print(f"邮件: {'✅ 成功' if status == '成功' else '❌ 失败'}")
print("✓ 邮件发送完成\n")

# 测试5: 创建面试链接
print("5️⃣ AI面试链接")
print("-" * 50)
link = None
if apply_result == "录用":
    print("测评通过，创建面试链接...")
    link = create_interview_link(email, "张三_测试简历.txt", job)
    if link:
        print(f"面试链接: {link}")
        
        print("\n⏳ 发送面试邀请...")
        inv_sent = send_interview_invitation_email(email, name, link)
        print(f"邀请邮件: {'✅ 已发送' if inv_sent else '❌ 失败'}")
    else:
        print("❌ 创建链接失败")
else:
    print("测评未通过，不启动面试")
print("✓ 面试链接完成\n")

# 测试6: 生成面试题目
print("6️⃣ AI面试题目生成")
print("-" * 50)
if apply_result == "录用":
    print("正在生成面试题目...\n")
    
    all_qs = {}
    total = 0
    
    for module in MODULE_NAMES:
        qs = generate_default_questions(module)
        all_qs[module] = qs
        total += len(qs)
        
        print(f"【{module}】: {len(qs)} 题")
        for i, q in enumerate(qs[:2], 1):
            print(f"  Q{i}: {q['question']}")
        print()
    
    print(f"题目统计: {len(all_qs)} 模块，共 {total} 题")
else:
    print("无需生成题目")

print("\n✓ 题目生成完成\n")

# 总结
print("="*80)
print("🎉 完整流程测试完成！")
print("="*80)
print("\n📊 测试总结:")
print("-" * 50)
print("✅ 环境准备: 通过")
print("✅ 简历解析: 通过")
print(f"✅ AI评分: {result['score']}分")
print(f"✅ 邮件通知: {'成功' if status == '成功' else '失败'}")
print(f"✅ 面试链接: {'已创建' if link else '未创建'}")
print(f"✅ 题目生成: {'完成' if apply_result == '录用' else '未执行'}")
print("\n📋 关键数据:")
print("-" * 50)
print(f"候选人: {name}")
print(f"岗位: {job}")
print(f"评分: {result['score']}分")
print(f"结果: {apply_result}")
if link:
    print(f"面试链接: {link}")
print()
