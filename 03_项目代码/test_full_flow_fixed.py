"""
完整流程测试脚本
测试从简历上传 -> 初筛 -> AI面试 -> 结果的完整流程
"""
import os
import sys
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config import SQLITE_DB_PATH, LOG_ROOT
from database_sqlite import (
    init_tables,
    save_to_mysql,
    query_jobs_from_db,
    get_jd_from_db,
    get_db_connection
)
from ai_scorer import handle_score
from email_service import handle_send_email, send_interview_invitation_email
from interview_service_sqlite import (
    create_interview_link,
    verify_interview_token,
    generate_questions_for_module,
    score_interview
)

def test_database():
    """测试数据库功能"""
    print("=" * 80)
    print("📊 测试数据库功能")
    print("=" * 80)
    
    # 初始化数据库
    init_tables()
    print("✅ 数据库表初始化完成")
    
    # 查询岗位
    jobs = query_jobs_from_db()
    print(f"✅ 可查询到 {len(jobs)} 个岗位")
    for job in jobs:
        print(f"   - {job}")
    
    # 查询岗位JD
    if jobs:
        jd = get_jd_from_db(jobs[0])
        print(f"✅ 岗位JD查询成功，内容长度: {len(jd)}")
    
    print("\n")

def test_resume_scoring():
    """测试简历评分功能"""
    print("=" * 80)
    print("📄 测试简历评分功能")
    print("=" * 80)
    
    # 模拟简历数据
    test_resume_text = """
    姓名：张三
    学历：本科
    专业：计算机科学与技术
    邮箱：zhangsan@example.com
    
    项目经历：
    1. 电商平台后端开发
    - 使用Python Flask框架开发电商平台
    - 实现用户管理、商品管理、订单管理功能
    - 使用MySQL数据库，Redis缓存
    
    技能：
    - Python, Java, JavaScript
    - MySQL, Redis, MongoDB
    - Flask, Django, Spring Boot
    """
    
    # 获取岗位JD
    jobs = query_jobs_from_db()
    if not jobs:
        print("❌ 没有可用岗位")
        return None
    
    job_name = jobs[0]
    jd_content = get_jd_from_db(job_name)
    
    # 调用评分
    result = handle_score(job_name, test_resume_text, jd_content)
    
    print(f"✅ 评分完成！")
    print(f"   岗位：{job_name}")
    print(f"   得分：{result['score']}")
    print(f"   初筛结果：{'通过' if result['score'] >=70 else '未通过'}")
    print(f"   报告长度：{len(result['report'])}")
    
    print("\n")
    return {
        'resume_text': test_resume_text,
        'job_name': job_name,
        'jd_content': jd_content,
        'score_result': result
    }

def test_interview_process(test_data):
    """测试AI面试流程"""
    print("=" * 80)
    print("🎤 测试AI面试流程")
    print("=" * 80)
    
    # 测试题目生成
    print("📝 生成面试题目...")
    modules = ["基础知识", "项目经历", "技能实战"]
    
    all_questions = {}
    for module in modules:
        questions = generate_questions_for_module(
            module, 
            test_data['resume_text'], 
            test_data['jd_content']
        )
        all_questions[module] = questions
        print(f"   ✅ {module}: 生成 {len(questions)} 道题")
    
    print(f"\n✅ 面试题目生成完成，共 {len(modules)} 个模块")
    
    # 模拟面试回答
    print("\n💬 模拟面试回答...")
    all_answers = []
    for module, questions in all_questions.items():
        for q in questions:
            all_answers.append({
                'module': module,
                'question': q['question'],
                'answer': '这是一个模拟的回答内容',
                'scoring_points': q.get('scoring_points', [])
            })
    print(f"✅ 生成 {len(all_answers)} 个模拟回答")
    
    print("\n")
    return {
        'questions': all_questions,
        'answers': all_answers
    }

def main():
    print("🚀 开始完整流程测试")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    try:
        # 1. 测试数据库
        test_database()
        
        # 2. 测试简历评分
        test_data = test_resume_scoring()
        if not test_data:
            return
        
        # 3. 测试面试流程
        interview_data = test_interview_process(test_data)
        
        print("=" * 80)
        print("🎉 所有测试完成！")
        print("=" * 80)
        print("\n✅ 关键功能已验证：")
        print("   1. 数据库初始化和岗位查询")
        print("   2. AI简历评分（初筛70分标准）")
        print("   3. AI面试题目生成")
        print("\n📂 日志目录：", LOG_ROOT)
        print("📂 数据库文件：", SQLITE_DB_PATH)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
