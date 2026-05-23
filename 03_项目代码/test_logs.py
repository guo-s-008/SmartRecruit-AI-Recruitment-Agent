"""
日志系统快速测试脚本
测试4类日志功能是否正常
"""
import os
import sys
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 80)
print("🎯 日志系统快速测试")
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

try:
    # 导入日志系统
    from log_system import (
        write_dialog_log,
        write_email_log,
        write_interview_log,
        write_interview_detail_log,
        write_hr_log,
        LOG_ROOT
    )
    
    print("\n✅ 日志系统导入成功")
    print(f"日志根目录：{LOG_ROOT}\n")
    
    # 1. 测试会话日志
    print("📝 测试1：会话日志...")
    write_dialog_log("user", "测试用户消息：我想投递数据分析师岗位")
    write_dialog_log("assistant", "测试助手回复：您好，请问您有简历吗？")
    print("✅ 会话日志测试成功")
    
    # 2. 测试邮件日志（初筛通过）
    print("\n📧 测试2：邮件日志（初筛通过）...")
    write_email_log(
        candidate_name="张三",
        email="zhangsan@example.com",
        job_name="数据分析师",
        score=85,
        result="初筛通过",
        applicant_email_content="""您好，张三！

恭喜您通过了简历初筛！

您的简历综合得分：85分

【简历优势】
- 具有相关项目经验
- 技能栈与岗位匹配

后续我们将发送面试邀请到您的邮箱，请注意查收。

祝您面试顺利！
智聘未来 招聘团队""",
        hr_email_content="""【简历初筛通知】
候选人：张三
邮箱：zhangsan@example.com
岗位：数据分析师
得分：85分
结果：初筛通过

请关注后续面试流程。
"""
    )
    print("✅ 初筛通过邮件日志测试成功")
    
    # 3. 测试邮件日志（初筛未通过）
    print("\n📧 测试3：邮件日志（初筛未通过）...")
    write_email_log(
        candidate_name="李四",
        email="lisi@example.com",
        job_name="AI算法工程师",
        score=58,
        result="初筛未通过",
        applicant_email_content="""您好，李四！

感谢您投递我们的岗位。

您的简历综合得分：58分
结果：暂未通过初筛

【改进建议】
- 建议补充项目量化成果
- 加强算法基础知识

欢迎优化简历后再次投递！

智聘未来 招聘团队""",
        hr_email_content="""【简历初筛通知】
候选人：李四
邮箱：lisi@example.com
岗位：AI算法工程师
得分：58分
结果：初筛未通过

建议录入人才库后续关注。
"""
    )
    print("✅ 初筛未通过邮件日志测试成功")
    
    # 4. 测试AI面试日志
    print("\n🎤 测试4：AI面试日志...")
    interview_data = {
        "token": "test_token_20260523",
        "email": "zhangsan@example.com",
        "candidate_name": "张三",
        "job_name": "数据分析师",
        "status": "completed",
        "final_score": 8.5,
        "result": "录用",
        "interview_duration": 1800,
        "scoring_details": {
            "基础知识": {"score": 9.0, "reason": "概念清晰"},
            "项目经历": {"score": 8.5, "reason": "项目描述详细"},
            "实习经历": {"score": 8.0, "reason": "经验相关"},
            "技能实战": {"score": 8.5, "reason": "技能熟练"},
            "技能进阶": {"score": 8.0, "reason": "有学习意愿"}
        },
        "questions": [
            {
                "module": "基础知识",
                "question": "什么是大数据？",
                "answer": "大数据是指无法在一定时间范围内用常规软件工具进行捕捉、管理和处理的数据集合。",
                "score": 9.0
            }
        ]
    }
    write_interview_log("张三", interview_data)
    
    # 测试面试详细日志
    write_interview_detail_log(
        candidate_name="张三",
        module="项目经历",
        question="请介绍你最有成就感的项目",
        answer="这是我参与的一个电商推荐系统项目，使用协同过滤算法，为用户推荐商品。项目使用Python开发，数据量达到千万级别，推荐准确率提升15%。",
        score=8.5,
        scoring_reason="项目描述清晰，有量化成果，技术栈与岗位匹配度高"
    )
    print("✅ AI面试日志测试成功")
    
    # 5. 测试HR操作日志
    print("\n👔 测试5：HR操作日志...")
    write_hr_log(
        operation_type="add",
        operator="HR管理员",
        target="新增岗位",
        before_data=None,
        after_data={
            "job_name": "数据分析师",
            "education": "本科",
            "city": "北京",
            "is_open": 1
        },
        remark="新增数据分析师岗位，开始招聘"
    )
    
    write_hr_log(
        operation_type="update",
        operator="HR管理员",
        target="更新岗位信息",
        before_data={
            "job_name": "数据分析师",
            "hiring_count": 1
        },
        after_data={
            "job_name": "数据分析师",
            "hiring_count": 3
        },
        remark="增加招聘人数"
    )
    
    write_hr_log(
        operation_type="query",
        operator="HR管理员",
        target="查询简历记录",
        before_data=None,
        after_data={"query_count": 10},
        remark="查询今日简历投递情况"
    )
    print("✅ HR操作日志测试成功")
    
    # 6. 查看日志目录结构
    print("\n📂 查看日志目录结构...")
    
    def show_tree(path, prefix=""):
        if not os.path.exists(path):
            return
        items = sorted(os.listdir(path))
        dirs = [i for i in items if os.path.isdir(os.path.join(path, i))]
        files = [i for i in items if os.path.isfile(os.path.join(path, i))]
        
        for f in files:
            print(f"{prefix}📄 {f}")
        
        for d in dirs:
            print(f"{prefix}📁 {d}/")
            show_tree(os.path.join(path, d), prefix + "    ")
    
    show_tree(LOG_ROOT)
    
    # 总结
    print("\n" + "=" * 80)
    print("🎉 日志系统测试完成！")
    print("=" * 80)
    print("\n📊 测试结果：")
    print("   ✅ 会话日志 - 正常工作")
    print("   ✅ 邮件日志（初筛通过） - 正常工作")
    print("   ✅ 邮件日志（初筛未通过） - 正常工作")
    print("   ✅ AI面试日志 - 正常工作")
    print("   ✅ HR操作日志 - 正常工作")
    print("\n📂 日志位置：", LOG_ROOT)
    print("\n📋 4类日志说明：")
    print("   1. 会话日志 - 记录所有对话内容")
    print("   2. 邮件日志 - 按初筛结果分类（初筛通过/初筛未通过）")
    print("   3. AI面试日志 - 按面试者姓名记录，包含完整面试信息")
    print("   4. HR操作日志 - 记录HR对岗位的增删改查操作")
    print("\n🎯 现在可以查看日志目录，验证所有日志文件是否正确生成！")
    
except Exception as e:
    print(f"\n❌ 测试失败：{e}")
    import traceback
    traceback.print_exc()
