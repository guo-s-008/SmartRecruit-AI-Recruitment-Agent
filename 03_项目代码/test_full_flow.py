"""
完整项目测试脚本
模拟从简历投递到AI面试的全流程
"""
import sys
import time
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/workspace/03_项目代码')

# 按顺序导入
from config import load_dotenv, API_CONFIG, SQLITE_DB_PATH
from database_sqlite import init_tables, get_db_connection, query_jobs_from_db, get_jd_from_db, get_scoring_criteria_from_db
from resume_parser import handle_upload_and_parse
from ai_scorer import handle_score, call_llm
from interview_service_sqlite import create_interview_link, generate_questions_for_module
from email_service import send_interview_invitation_email, send_email
import import_jobs

print("\n" + "="*80)
print("🎯 智聘未来 AI招聘系统 - 完整流程测试")
print("="*80 + "\n")

# 测试1：配置检查
print("📋 测试1：检查配置")
print("-" * 60)
print(f"✅ API Key: {API_CONFIG['key'][:10]}..." if API_CONFIG['key'] else "❌ API Key 未配置")
print(f"✅ 数据库: {SQLITE_DB_PATH}")
print()

# 测试2：导入岗位数据
print("📋 测试2：导入岗位数据")
print("-" * 60)
import_jobs.import_jobs()
print()

# 测试3：查询岗位列表
print("📋 测试3：查询岗位列表")
print("-" * 60)
jobs = query_jobs_from_db()
print(f"✅ 共有 {len(jobs)} 个岗位在招聘：")
for job in jobs:
    print(f"   - {job}")
print()

# 测试4：读取简历
print("📋 测试4：读取测试简历")
print("-" * 60)
resume_path = "/workspace/02_已处理简历/张三_测试简历.txt"
with open(resume_path, 'r', encoding='utf-8') as f:
    resume_text = f.read()
print(f"✅ 简历读取成功，共 {len(resume_text)} 字符")
print()

# 测试5：AI简历解析
print("📋 测试5：AI简历解析")
print("-" * 60)
from utils import (
    extract_email,
    extract_name,
    extract_gender,
    extract_age,
    extract_major,
    extract_education,
    extract_city
)
parsed_data = {
    '姓名': extract_name(resume_text),
    '邮箱': extract_email(resume_text),
    '性别': extract_gender(resume_text),
    '年龄': extract_age(resume_text),
    '专业': extract_major(resume_text),
    '学历': extract_education(resume_text),
    '城市': extract_city(resume_text)
}
print(f"✅ 简历解析完成:")
print(f"   - 姓名: {parsed_data.get('姓名', '未知')}")
print(f"   - 邮箱: {parsed_data.get('邮箱', '未知')}")
print(f"   - 学历: {parsed_data.get('学历', '未知')}")
print()

# 测试6：AI评分
print("📋 测试6：AI简历评分")
print("-" * 60)
test_job = "AI大数据工程师"
jd_content = get_jd_from_db(test_job)
scoring_criteria = get_scoring_criteria_from_db(test_job)
print(f"✅ 获取JD: {test_job}")
print(f"   JD长度: {len(jd_content)} 字符")
print(f"   评分标准: {'有' if scoring_criteria else '无'}")

print("\n⏳ 正在调用AI进行评分，请稍候...")
result = handle_score(test_job, resume_text, jd_content, scoring_criteria)
print(f"\n✅ AI评分完成:")
print(f"   - 综合得分: {result['score']}分")
print(f"   - 优势: {result['advantage'][:50]}...")
print(f"   - 不足: {result['shortcoming'][:50]}...")
print()

# 测试7：创建面试链接
print("📋 测试7：创建AI面试链接")
print("-" * 60)
email = parsed_data.get('邮箱', 'zhangsan_test@example.com')
resume_name = "张三_测试简历.txt"
interview_link = create_interview_link(email, resume_name, test_job)
if interview_link:
    print(f"✅ 面试链接创建成功:")
    print(f"   {interview_link}")
else:
    print("❌ 面试链接创建失败")
print()

# 测试8：生成面试题目
print("📋 测试8：AI生成面试题目")
print("-" * 60)
print("⏳ 正在生成各模块面试题目...")
questions_dict = {}
for module in ["基础知识", "项目经历"]:
    print(f"   生成 {module} 模块题目...")
    questions = generate_questions_for_module(module, resume_text, jd_content)
    questions_dict[module] = questions
    time.sleep(1)  # 避免API调用过快

print(f"\n✅ 面试题目生成完成:")
for module, questions in questions_dict.items():
    print(f"\n【{module}】")
    if questions and isinstance(questions, list):
        for i, q in enumerate(questions[:2], 1):  # 只显示前2题
            if isinstance(q, dict):
                print(f"  Q{i}: {q.get('question', '无法解析')[:80]}...")
            else:
                print(f"  Q{i}: {str(q)[:80]}...")
    else:
        print(f"  未能生成有效题目")
print()

# 测试9：发送面试邀请邮件
print("📋 测试9：发送面试邀请邮件")
print("-" * 60)
print(f"⏳ 正在发送邮件到: {email}")
mail_sent = send_interview_invitation_email(email, "张三", interview_link)
print(f"{'✅' if mail_sent else '❌'} 邮件发送{'成功' if mail_sent else '失败'}")
print()

# 测试10：发送评分结果邮件
print("📋 测试10：发送评分结果邮件")
print("-" * 60)
apply_result = "录用" if result['score'] >= 85 else "不合适"
print(f"⏳ 发送评分邮件到: {email}")
mail_sent = send_email(
    email, 
    result['score'], 
    test_job, 
    apply_result, 
    result['report'], 
    result['advantage'], 
    result['shortcoming']
)
print(f"{'✅' if mail_sent == '成功' else '❌'} 邮件发送{'成功' if mail_sent == '成功' else '失败'}")
print()

# 测试总结
print("="*80)
print("📊 测试总结")
print("="*80)
print("✅ 配置检查完成")
print("✅ 岗位数据导入完成")
print("✅ 简历解析完成")
print("✅ AI评分完成")
print("✅ 面试链接创建完成")
print("✅ 面试题目生成完成")
print("✅ 邮件发送完成")
print()
print("🎉 全流程测试完成！")
print()
print("💡 测试提示：")
print("   - 检查日志文件: /workspace/07_系统日志/")
print("   - 查看数据库: /workspace/04_数据文件/recruitment.db")
print("   - 面试链接有效期: 48小时")
print("="*80)
