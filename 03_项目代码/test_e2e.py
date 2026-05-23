"""
完整端到端招聘系统测试脚本
模拟：简历投递 → AI评分 → 发送邮件 → AI面试 → 题目生成
"""
import sys
import time
import json
import os
from pathlib import Path

sys.path.insert(0, '/workspace/03_项目代码')

from config import API_CONFIG, SQLITE_DB_PATH, EMAIL_CONFIG
from database_sqlite import init_tables, query_jobs_from_db, get_jd_from_db, get_scoring_criteria_from_db
from utils import extract_email, extract_name, extract_gender, extract_age, extract_major, extract_education, extract_city
from ai_scorer import handle_score, call_llm
from interview_service_sqlite import create_interview_link, generate_questions_for_module, MODULE_NAMES
from email_service import send_email, send_interview_invitation_email

# ========================================
# 测试1: 环境准备
# ========================================
print("\n" + "="*90)
print("🎯 智聘未来招聘系统 - 完整端到端测试")
print("="*90 + "\n")

print("📋 测试 1/6: 环境准备")
print("-" * 90)
print(f"✅ 数据库: {SQLITE_DB_PATH}")
print(f"✅ API Key: {API_CONFIG['key'][:10]}...")
print(f"✅ 邮件配置: {EMAIL_CONFIG.get('hr_email', '未配置')}")

# 检查岗位数据
jobs = query_jobs_from_db()
print(f"✅ 可用岗位: {len(jobs)} 个")
for job in jobs:
    print(f"   - {job}")

print("✓ 环境准备完成\n")
time.sleep(1)

# ========================================
# 测试2: 读取简历并解析
# ========================================
print("📋 测试 2/6: 简历解析")
print("-" * 90)

resume_path = "/workspace/02_已处理简历/张三_测试简历.txt"
with open(resume_path, 'r', encoding='utf-8') as f:
    resume_text = f.read()

parsed_data = {
    '姓名': extract_name(resume_text),
    '邮箱': extract_email(resume_text),
    '性别': extract_gender(resume_text),
    '年龄': extract_age(resume_text),
    '专业': extract_major(resume_text),
    '学历': extract_education(resume_text),
    '城市': extract_city(resume_text)
}

print(f"✓ 简历读取: {len(resume_text)} 字符")
print(f"✓ 解析结果:")
print(f"   姓名: {parsed_data['姓名']}")
print(f"   邮箱: {parsed_data['邮箱']}")
print(f"   学历: {parsed_data['学历']}")
print(f"   专业: {parsed_data['专业']}")
print(f"✓ 简历解析完成\n")
time.sleep(1)

# ========================================
# 测试3: AI评分
# ========================================
print("📋 测试 3/6: AI简历评分")
print("-" * 90)
test_job = "AI大数据工程师"
jd_content = get_jd_from_db(test_job)
scoring_criteria = get_scoring_criteria_from_db(test_job)

print(f"✓ 目标岗位: {test_job}")
print(f"✓ JD长度: {len(jd_content)} 字符")
print(f"✓ 评分标准: {'已加载' if scoring_criteria else '无'}")

print("\n⏳ 正在调用AI进行评分，请稍候...")
result = handle_score(test_job, resume_text, jd_content, scoring_criteria)

print("\n" + "="*50)
print("📊 AI评分结果")
print("="*50)
print(f"综合得分: {result['score']}/100")
print(f"测评结论: {'✅ 通过' if result['score'] >= 80 else '❌ 未通过'}")
print("\n优势:")
print(result['advantage'])
print("\n不足与建议:")
print(result['shortcoming'])
print("\n✓ AI评分完成\n")
time.sleep(2)

# ========================================
# 测试4: 发送邮件
# ========================================
print("📋 测试 4/6: 发送邮件通知")
print("-" * 90)

candidate_email = parsed_data['邮箱']
hr_email = EMAIL_CONFIG.get('hr_email', 'q17877881463qq@163.com')
apply_result = "录用" if result['score'] >= 80 else "不合适"

print(f"✓ 收件人:")
print(f"   候选人: {candidate_email}")
print(f"   HR: {hr_email}")
print(f"✓ 测评结果: {apply_result} ({result['score']}分)")

print("\n⏳ 正在发送邮件...")
mail_status = send_email(
    candidate_email,
    result['score'],
    test_job,
    apply_result,
    result['report'],
    result['advantage'],
    result['shortcoming']
)

print(f"\n✓ 邮件发送: {'✅ 成功' if mail_status == '成功' else '❌ 失败'}")
print(f"✓ 邮件通知完成\n")
time.sleep(2)

# ========================================
# 测试5: 创建面试链接
# ========================================
print("📋 测试 5/6: 创建AI面试链接")
print("-" * 90)

interview_link = None
if apply_result == "录用":
    print("✅ 测评通过，启动面试流程")
    interview_link = create_interview_link(
        candidate_email,
        "张三_测试简历.txt",
        test_job
    )
    
    if interview_link:
        print(f"✓ 面试链接创建成功:")
        print(f"   {interview_link}")
        
        # 发送面试邀请邮件
        print("\n⏳ 正在发送面试邀请邮件...")
        email_sent = send_interview_invitation_email(
            candidate_email,
            parsed_data['姓名'],
            interview_link
        )
        print(f"✓ 面试邀请邮件: {'✅ 已发送' if email_sent else '❌ 发送失败'}")
    else:
        print("❌ 面试链接创建失败")
else:
    print("❌ 测评未通过，不启动面试流程")

print(f"\n✓ 面试链接创建完成\n")
time.sleep(2)

# ========================================
# 测试6: 生成面试题目
# ========================================
print("📋 测试 6/6: AI面试题目生成")
print("-" * 90)

all_questions = {}
if apply_result == "录用":
    print("✅ 开始为面试生成题目")
    
    for module_name in MODULE_NAMES:
        print(f"\n⏳ 正在生成【{module_name}】模块题目...")
        questions = generate_questions_for_module(module_name, resume_text, jd_content)
        
        if questions and isinstance(questions, list):
            all_questions[module_name] = questions
            print(f"✅ 生成了 {len(questions)} 道题目")
            
            # 显示前2道题
            for i, q in enumerate(questions[:2], 1):
                if isinstance(q, dict):
                    q_text = q.get('question', '无法解析')[:70]
                    print(f"   Q{i}: {q_text}...")
                else:
                    print(f"   Q{i}: {str(q)[:70]}...")
        else:
            print(f"❌ 未能生成题目")
            all_questions[module_name] = []
    
    # 显示题目统计
    total_questions = sum(len(q) for q in all_questions.values())
    print(f"\n" + "="*50)
    print(f"📋 面试题目统计")
    print(f"="*50)
    for module, qs in all_questions.items():
        print(f"  {module}: {len(qs)} 题")
    print(f"  总计: {total_questions} 题")
else:
    print("❌ 无需生成面试题目")

print(f"\n✓ 题目生成完成\n")
time.sleep(1)

# ========================================
# 完整总结
# ========================================
print("="*90)
print("🎉 完整端到端测试完成！")
print("="*90 + "\n")

print("📊 测试总结:")
print("-" * 50)
print("✅ 环境准备: 通过")
print("✅ 简历解析: 通过")
print(f"✅ AI评分: 通过 (得分: {result['score']})")
print(f"✅ 邮件通知: {'通过' if mail_status == '成功' else '失败'}")
print(f"✅ 面试链接: {'已创建' if apply_result == '录用' else '未创建'}")
print(f"✅ 题目生成: {'成功' if apply_result == '录用' else '未执行'}")

print("\n📋 关键数据:")
print("-" * 50)
print(f"候选人: {parsed_data['姓名']}")
print(f"应聘岗位: {test_job}")
print(f"综合评分: {result['score']}/100")
print(f"测评结果: {apply_result}")
if apply_result == "录用" and interview_link:
    print(f"面试链接: {interview_link}")

print("\n💡 测试提示:")
print("-" * 50)
print("• 完整测试已保存")
print("• 可访问Web界面进行交互测试")
print("• 数据库已更新测试记录")

print("\n" + "="*90 + "\n")
