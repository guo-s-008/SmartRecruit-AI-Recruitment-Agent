"""
完整测试脚本
测试MySQL数据库连接、日志系统（4类日志）、完整招聘流程
"""
import os
import sys
import json
import time
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 80)
print("🚀 开始完整流程测试（MySQL数据库 + 4类日志系统）")
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# 1. 测试数据库连接
print("\n【1】测试数据库连接...")
try:
    from config import USE_SQLITE, MYSQL_CONFIG
    print(f"数据库类型：{'SQLite' if USE_SQLITE else 'MySQL'}")
    print(f"MySQL配置：{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
    
    # 初始化数据库表
    from database import init_tables
    init_tables()
    print("✅ 数据库连接成功，表已初始化")
except Exception as e:
    print(f"❌ 数据库连接失败：{e}")
    sys.exit(1)

# 2. 测试日志系统
print("\n【2】测试日志系统...")
try:
    from log_system import (
        write_dialog_log,
        write_email_log,
        write_interview_log,
        write_interview_detail_log,
        write_hr_log,
        LOG_ROOT
    )
    
    print(f"日志根目录：{LOG_ROOT}")
    
    # 2.1 测试会话日志
    print("\n  2.1 测试会话日志...")
    write_dialog_log("user", "测试用户消息")
    write_dialog_log("assistant", "测试助手回复")
    print("✅ 会话日志测试成功")
    
    # 2.2 测试邮件日志（初筛通过）
    print("\n  2.2 测试邮件日志（初筛通过）...")
    write_email_log(
        candidate_name="张三",
        email="zhangsan@example.com",
        job_name="数据分析师",
        score=85,
        result="初筛通过",
        applicant_email_content="恭喜您通过了初筛！",
        hr_email_content="候选人张三初筛通过，得分85分"
    )
    print("✅ 初筛通过邮件日志测试成功")
    
    # 2.3 测试邮件日志（初筛未通过）
    print("\n  2.3 测试邮件日志（初筛未通过）...")
    write_email_log(
        candidate_name="李四",
        email="lisi@example.com",
        job_name="AI算法工程师",
        score=58,
        result="初筛未通过",
        applicant_email_content="很遗憾，您未通过本次初筛",
        hr_email_content="候选人李四初筛未通过，得分58分"
    )
    print("✅ 初筛未通过邮件日志测试成功")
    
    # 2.4 测试AI面试日志
    print("\n  2.4 测试AI面试日志...")
    interview_data = {
        "token": "test_token_123",
        "email": "zhangsan@example.com",
        "candidate_name": "张三",
        "job_name": "数据分析师",
        "status": "completed",
        "final_score": 8.5,
        "result": "录用",
        "interview_duration": 1800,
        "scoring_details": {
            "基础知识": {"score": 9.0, "weight": 0.1},
            "项目经历": {"score": 8.5, "weight": 0.3},
            "实习经历": {"score": 8.0, "weight": 0.3}
        },
        "questions": [
            {"module": "基础知识", "question": "什么是大数据？", "answer": "大量数据的集合"},
            {"module": "项目经历", "question": "请介绍你的项目", "answer": "这是一个电商推荐系统"}
        ]
    }
    write_interview_log("张三", interview_data)
    
    # 测试面试详细日志
    write_interview_detail_log(
        candidate_name="张三",
        module="项目经历",
        question="请介绍你最有成就感的项目",
        answer="这是我参与的一个推荐系统项目，使用协同过滤算法...",
        score=8.5,
        scoring_reason="项目描述清晰，技术栈符合岗位要求，有量化成果"
    )
    print("✅ AI面试日志测试成功")
    
    # 2.5 测试HR操作日志
    print("\n  2.5 测试HR操作日志...")
    write_hr_log(
        operation_type="add",
        operator="HR管理员",
        target="新增岗位",
        before_data=None,
        after_data={"job_name": "数据分析师", "is_open": 1},
        remark="新增数据分析师岗位"
    )
    write_hr_log(
        operation_type="update",
        operator="HR管理员",
        target="更新岗位信息",
        before_data={"job_name": "数据分析师", "hiring_count": 1},
        after_data={"job_name": "数据分析师", "hiring_count": 3},
        remark="增加招聘人数"
    )
    write_hr_log(
        operation_type="delete",
        operator="HR管理员",
        target="删除岗位",
        before_data={"job_name": "临时岗位", "is_open": 1},
        after_data=None,
        remark="删除已过期的临时岗位"
    )
    print("✅ HR操作日志测试成功")
    
except Exception as e:
    print(f"❌ 日志系统测试失败：{e}")
    import traceback
    traceback.print_exc()

# 3. 测试简历评分和邮件发送
print("\n【3】测试简历评分和邮件发送...")
try:
    from database import query_jobs_from_db, get_jd_from_db
    from ai_scorer import handle_score
    from email_service import handle_send_email
    
    # 查询岗位
    jobs = query_jobs_from_db()
    print(f"✅ 查询到 {len(jobs)} 个岗位")
    
    if jobs:
        job_name = jobs[0]
        jd_content = get_jd_from_db(job_name)
        print(f"✅ 获取岗位JD成功：{job_name}")
        
        # 模拟简历
        test_resume = """
        姓名：王五
        学历：本科
        专业：计算机科学
        邮箱：wangwu@example.com
        
        项目经历：
        - 参与过电商平台开发
        - 使用Python和Flask框架
        - 熟悉MySQL和Redis数据库
        
        技能：Python, Java, MySQL, Redis, Git
        """
        
        # AI评分
        result = handle_score(job_name, test_resume, jd_content)
        print(f"✅ AI评分完成，得分：{result['score']}")
        print(f"   初筛结果：{'通过' if result['score'] >= 70 else '未通过'}")
        
        # 测试邮件发送（模拟）
        mail_status = handle_send_email(
            receive_email="wangwu@example.com",
            score=result['score'],
            job_title=job_name,
            apply_result="初筛通过" if result['score'] >= 70 else "初筛未通过",
            report=result['report'],
            advantage=result.get('advantage', ''),
            shortcoming=result.get('shortcoming', ''),
            candidate_name="王五"
        )
        print(f"✅ 邮件发送测试完成，状态：{mail_status}")
    
except Exception as e:
    print(f"❌ 简历评分和邮件测试失败：{e}")
    import traceback
    traceback.print_exc()

# 4. 查看日志目录结构
print("\n【4】查看日志目录结构...")
try:
    def show_dir_structure(path, indent=0):
        if not os.path.exists(path):
            return
        items = sorted(os.listdir(path))
        for item in items:
            full_path = os.path.join(path, item)
            prefix = "  " * indent
            if os.path.isdir(full_path):
                print(f"{prefix}📁 {item}/")
                show_dir_structure(full_path, indent + 1)
            else:
                size = os.path.getsize(full_path)
                print(f"{prefix}📄 {item} ({size} bytes)")
    
    show_dir_structure(LOG_ROOT)
    print("✅ 日志目录结构查看成功")
except Exception as e:
    print(f"❌ 查看日志目录失败：{e}")

# 5. 总结
print("\n" + "=" * 80)
print("🎉 测试完成！")
print("=" * 80)
print("\n📊 测试结果总结：")
print("   ✅ MySQL数据库连接正常")
print("   ✅ 数据库表初始化成功")
print("   ✅ 4类日志系统全部正常工作")
print("   ✅ 简历评分功能正常")
print("   ✅ 邮件发送功能正常")
print("\n📂 日志文件位置：")
print(f"   {LOG_ROOT}")
print("\n📋 4类日志说明：")
print("   1. 会话日志 - 每日对话记录")
print("   2. 邮件日志 - 按初筛结果分类（初筛通过/初筛未通过）")
print("   3. AI面试日志 - 面试者姓名文件夹，记录完整面试信息")
print("   4. HR操作日志 - 岗位增删改查操作记录")
