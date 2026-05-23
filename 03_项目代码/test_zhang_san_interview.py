
#!/usr/bin/env python3
"""
张三的完整AI面试流程测试脚本
"""
import os
import sys
import json
from datetime import datetime, timedelta

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import USE_SQLITE
from log_system import (
    write_interview_log,
    write_email_log,
    write_dialog_log,
    write_recruit_log
)
from interview_service_sqlite import (
    create_interview_link,
    generate_questions_for_module,
    update_module_questions,
    score_interview,
    MODULE_NAMES
)
from database_sqlite import (
    save_to_mysql,
    save_interview_url,
    update_interview_url_request,
    get_db_connection,
    init_tables
)
from email_service import (
    send_interview_invitation_email,
    send_interview_interrupted_email
)

# 张三的简历内容
ZHANG_SAN_RESUME = """
张三
简历
电话：13888888888  邮箱：zhangsan@example.com  地址：北京市海淀区

教育背景
北京大学 - 计算机科学与技术 - 本科 - 2018.09 - 2022.06
- 主修课程：数据结构、算法、计算机网络、操作系统、机器学习
- GPA：3.8/4.0
- 优秀学生奖学金 (2019、2020)

实习经历
1. 字节跳动 - 后端开发实习 - 2021.06 - 2021.09
- 参与抖音推荐系统的后端开发
- 使用Python和Go语言开发微服务接口
- 优化了API响应时间，从300ms降低到150ms
- 使用Redis进行缓存优化

2. 阿里巴巴 - 大数据实习 - 2020.07 - 2020.09
- 参与用户行为分析系统开发
- 使用Hadoop和Spark进行大数据处理
- 编写ETL任务处理每天10TB级别的数据
- 使用MySQL和Hive存储数据

项目经历
1. 校园二手交易平台 - 后端负责人
- 开发完整的后端系统，使用Python + Django框架
- 实现用户认证、商品发布、交易、消息通知等功能
- 使用Redis缓存热点数据，QPS提升5倍
- 用户数：1000+，月活跃：500+

2. 个人知识图谱构建 - 独立项目
- 使用自然语言处理技术从网页中提取知识
- 构建了包含10万个实体的知识图谱
- 使用Neo4j图数据库存储和查询
- 实现简单的问答系统

技术技能
- 编程语言：Python、Java、Go、JavaScript
- 大数据：Hadoop、Spark、Hive、Flink
- 数据库：MySQL、PostgreSQL、Redis、MongoDB、Neo4j
- 机器学习：Scikit-learn、TensorFlow、PyTorch
- 工具：Git、Docker、Linux、Kubernetes
"""

# 张三的面试回答（模拟）
ZHANG_SAN_ANSWERS = {
    "基础知识": [
        {
            "question": "请介绍一下你所学专业的核心课程有哪些？",
            "answer": "我在计算机科学与技术专业学习的核心课程包括数据结构、算法设计与分析、计算机网络、操作系统、机器学习等。"
        },
        {
            "question": "你掌握的编程语言有哪些？请举例说明项目中如何使用的。",
            "answer": "我掌握的编程语言有Python、Java、Go和JavaScript。在字节跳动实习时，我使用Python和Go开发了推荐系统的后端接口。"
        },
        {
            "question": "数据库的ACID特性是什么？请简要解释。",
            "answer": "ACID指的是原子性(Atomicity)、一致性(Consistency)、隔离性(Isolation)和持久性(Durability)，是保证数据库事务可靠性的四个特性。"
        }
    ],
    "项目经历": [
        {
            "question": "请介绍你参与过的最有代表性的项目。",
            "answer": "校园二手交易平台是我最有代表性的项目。作为后端负责人，我负责整个后端系统的架构设计和开发。"
        },
        {
            "question": "项目中遇到的最大挑战是什么？如何解决的？",
            "answer": "最大的挑战是当用户量增加时系统响应变慢。我使用Redis缓存热点数据，QPS提升了5倍，解决了这个问题。"
        },
        {
            "question": "你在项目中的角色是什么？有哪些具体贡献？",
            "answer": "我是项目的后端负责人，负责架构设计、核心功能开发、性能优化等。我的贡献包括用户认证、商品发布、交易系统等模块。"
        }
    ],
    "实习经历": [
        {
            "question": "你在实习期间主要负责什么工作？",
            "answer": "在字节跳动实习时，我主要负责抖音推荐系统的后端开发，参与微服务接口的设计和实现。在阿里巴巴实习时，参与用户行为分析系统开发。"
        },
        {
            "question": "实习期间学到了哪些最有价值的技能？",
            "answer": "我学到了大规模分布式系统的设计、微服务架构、性能优化等实用技能，还有团队协作和沟通能力也有很大提升。"
        }
    ],
    "技能实战": [
        {
            "question": "请描述一次你解决技术难题的经历。",
            "answer": "在字节跳动实习时，我负责优化一个API接口的响应时间。通过分析代码和数据库查询，我发现了几个性能瓶颈，优化后从300ms降低到150ms。"
        },
        {
            "question": "你最擅长的技术领域是什么？为什么？",
            "answer": "我最擅长后端开发和大数据处理。因为我有两个相关的实习经历，还有多个项目实践，这方面经验丰富。"
        },
        {
            "question": "如何保证代码质量？你通常会做哪些检查？",
            "answer": "我会做单元测试、代码评审、静态分析工具检查，以及遵循代码规范。在提交代码前会进行全面的测试。"
        }
    ],
    "技能进阶实战": [
        {
            "question": "你对未来的技术发展方向有什么规划？",
            "answer": "我希望在人工智能和大数据领域深入发展，特别是大模型应用和推荐系统方向，我想继续在这个领域深耕。"
        },
        {
            "question": "如果遇到技术瓶颈，你会如何突破？",
            "answer": "我会先查阅官方文档和论文，然后看有没有开源实现，也会向有经验的同事请教，最后通过实验来验证方案。"
        },
        {
            "question": "你如何看待技术创新与业务需求之间的关系？",
            "answer": "技术创新应该服务于业务需求，但好的技术创新也能创造新的业务场景。两者是相互促进的关系。"
        }
    ]
}

def init_test_database():
    """初始化测试数据库"""
    print("=" * 80)
    print("📊 初始化数据库...")
    print("=" * 80)
    init_tables()
    print("✅ 数据库初始化完成\n")

def save_zhang_san_resume(job_name="数据分析师"):
    """保存张三的简历记录"""
    print("=" * 80)
    print("📄 保存张三的简历记录...")
    print("=" * 80)
    
    # 模拟解析后的简历数据
    detail_data = {
        "投递时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "姓名": "张三",
        "性别": "男",
        "年龄": "24",
        "学历": "本科",
        "专业": "计算机科学与技术",
        "所在城市": "北京",
        "意向地区": "北京",
        "岗位": job_name,
        "得分": 85,
        "邮箱": "zhangsan@example.com",
        "邮件状态": "成功",
        "测评结果": "初筛通过"
    }
    
    resume_id = save_to_mysql(detail_data)
    
    # 记录招聘日志
    write_recruit_log(
        resume_name="张三简历.pdf",
        job_name=job_name,
        score=85,
        email="zhangsan@example.com",
        mail_status="成功",
        result_status="初筛通过"
    )
    
    print(f"✅ 简历记录已保存，ID: {resume_id}\n")
    return resume_id, detail_data

def create_zhang_san_interview(resume_id, detail_data):
    """创建张三的面试链接"""
    print("=" * 80)
    print("🔗 创建张三的面试链接...")
    print("=" * 80)
    
    interview_url = create_interview_link(
        email="zhangsan@example.com",
        resume_name="张三简历.pdf",
        job_name=detail_data["岗位"],
        resume_id=resume_id,
        candidate_name="张三"
    )
    
    if interview_url:
        token = interview_url.split("token=")[-1]
        # 保存面试URL
        save_interview_url(resume_id, interview_url, token)
        
        # 模拟发送面试邀请邮件
        print(f"✅ 面试链接已创建: {interview_url}")
        
        # 记录邮件日志
        email_content = f"""
张三：

恭喜你，你的简历已通过初筛！
请在48小时内完成AI面试。

面试链接：{interview_url}

⚠️ 重要提醒：该面试链接最多只能访问3次，超过3次后将失效，请确保网络稳定！

智聘未来 招聘团队
        """
        
        write_email_log(
            candidate_name="张三",
            email="zhangsan@example.com",
            job_name=detail_data["岗位"],
            score=85,
            result="初筛通过",
            applicant_email_content=email_content,
            hr_email_content=f"面试邀请已发送给 张三 (zhangsan@example.com)"
        )
        
        print("✅ 面试邀请邮件已记录到日志\n")
        return interview_url, token
    else:
        print("❌ 面试链接创建失败\n")
        return None, None

def generate_zhang_san_questions(token, job_name):
    """为张三生成面试题目"""
    print("=" * 80)
    print("🧠 为张三生成AI面试题目...")
    print("=" * 80)
    
    # 获取JD（使用模拟数据）
    jd_content = f"""
{job_name}
岗位要求：
1. 扎实的计算机基础知识
2. 熟练掌握Python编程
3. 有大数据和数据分析经验
4. 熟悉SQL和数据库操作
5. 有项目经验者优先
    """
    
    all_questions = {}
    
    for module_name in MODULE_NAMES:
        print(f"\n📝 正在生成 [{module_name}] 模块题目...")
        
        try:
            # 先使用默认题目（不实际调用LLM）
            questions = ZHANG_SAN_ANSWERS[module_name]
            # 转换格式
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question": q["question"],
                    "reference_answer": "",
                    "scoring_points": ["知识掌握", "表达清晰"]
                })
            
            # 保存题目到数据库
            update_module_questions(token, module_name, formatted_questions)
            
            all_questions[module_name] = formatted_questions
            print(f"✅ {module_name} 模块题目已生成并保存，共 {len(formatted_questions)} 题")
        except Exception as e:
            print(f"❌ 生成题目失败: {e}")
    
    print("\n✅ 所有面试题目生成完成！\n")
    return all_questions

def simulate_zhang_san_answers(token, questions, job_name):
    """模拟张三完成面试"""
    print("=" * 80)
    print("💬 模拟张三完成AI面试...")
    print("=" * 80)
    
    # 模拟访问URL 3次
    print("\n🔄 模拟访问面试链接（第一次）...")
    is_interrupted, request_count = update_interview_url_request(token)
    print(f"   请求次数: {request_count}, 是否中断: {is_interrupted}")
    
    print("🔄 模拟访问面试链接（第二次）...")
    is_interrupted, request_count = update_interview_url_request(token)
    print(f"   请求次数: {request_count}, 是否中断: {is_interrupted}")
    
    # 收集所有答案
    all_answers = []
    for module_name in MODULE_NAMES:
        print(f"\n📋 回答 [{module_name}] 模块...")
        if module_name in ZHANG_SAN_ANSWERS:
            module_questions = questions.get(module_name, [])
            module_answers = ZHANG_SAN_ANSWERS[module_name]
            
            for i, (q, a) in enumerate(zip(module_questions, module_answers)):
                answer_record = {
                    "module": module_name,
                    "question": a["question"],
                    "answer": a["answer"],
                    "reference_answer": q.get("reference_answer", ""),
                    "scoring_points": q.get("scoring_points", [])
                }
                all_answers.append(answer_record)
                print(f"   问题 {i+1}: {a['question']}")
                print(f"   回答: {a['answer']}")
    
    print(f"\n✅ 张三已完成全部 {len(all_answers)} 道题目！")
    return all_answers

def score_zhang_san_interview(token, all_answers, job_name):
    """为张三的面试评分"""
    print("\n" + "=" * 80)
    print("📊 AI为张三面试评分...")
    print("=" * 80)
    
    # 获取面试记录
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interview_record WHERE token=?", (token,))
    row = cursor.fetchone()
    
    if row:
        cursor.execute("PRAGMA table_info(interview_record)")
        columns = [col[1] for col in cursor.fetchall()]
        record = dict(zip(columns, row))
        
        # 模拟评分（不实际调用LLM）
        print("\n📝 各模块评分：")
        module_scores = {
            "基础知识": 9.0,
            "项目经历": 9.5,
            "实习经历": 9.2,
            "技能实战": 8.8,
            "技能进阶实战": 8.5
        }
        
        for module, score in module_scores.items():
            print(f"   {module}: {score}/10")
        
        total_score = sum([
            9.0 * 0.1,
            9.5 * 0.3,
            9.2 * 0.3,
            8.8 * 0.2,
            8.5 * 0.1
        ])
        
        apply_result = "录用" if total_score >= 8 else "不合适"
        print(f"\n🎯 最终得分: {total_score:.1f}/10")
        print(f"🏆 面试结果: {apply_result}")
        
        # 保存面试记录日志
        scoring_details = {
            module: {"score": score, "reason": f"{module}表现优秀"} 
            for module, score in module_scores.items()
        }
        
        # 转换为需要的格式
        questions_list = []
        for module_name, module_answers in ZHANG_SAN_ANSWERS.items():
            for ans in module_answers:
                questions_list.append({
                    "module": module_name,
                    "question": ans["question"],
                    "answer": ans["answer"],
                    "score": scoring_details[module_name]["score"]
                })
        
        interview_duration = 1800  # 30分钟
        
        write_interview_log(
            candidate_name="张三",
            email="zhangsan@example.com",
            job_name=job_name,
            token=token,
            questions=questions_list,
            final_score=total_score,
            scoring_details=scoring_details,
            result=apply_result,
            interview_duration=interview_duration
        )
        
        print("\n✅ 面试评分完成！")
        print("✅ 面试记录已保存到日志！\n")
        
        # 更新数据库
        cursor.execute(
            "UPDATE interview_record SET final_score=?, result=?, status='completed' WHERE token=?",
            (total_score, apply_result, token)
        )
        conn.commit()
        
        return module_scores, total_score, apply_result
    else:
        print("❌ 未找到面试记录")
        return None, None, None

def show_logs():
    """展示生成的所有日志"""
    print("=" * 80)
    print("📋 完整日志内容展示")
    print("=" * 80)
    
    log_root = os.path.join(current_dir, "..", "07_系统日志")
    
    # 查看interview_logs目录
    interview_log_path = os.path.join(log_root, "interview_logs", "张三")
    if os.path.exists(interview_log_path):
        print(f"\n📂 面试日志 (张三):")
        print("-" * 80)
        
        for filename in os.listdir(interview_log_path):
            filepath = os.path.join(interview_log_path, filename)
            if os.path.isfile(filepath):
                print(f"\n📄 {filename}:")
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)
    
    # 查看email_logs
    email_log_path = os.path.join(log_root, "log_email")
    if os.path.exists(email_log_path):
        print(f"\n📂 邮件日志:")
        print("-" * 80)
        
        for date_dir in os.listdir(email_log_path):
            date_path = os.path.join(email_log_path, date_dir)
            if os.path.isdir(date_path):
                for status_dir in os.listdir(date_path):
                    status_path = os.path.join(date_path, status_dir)
                    if os.path.isdir(status_path):
                        for filename in os.listdir(status_path):
                            if "张三" in filename:
                                filepath = os.path.join(status_path, filename)
                                print(f"\n📄 {filename} (路径: {date_dir}/{status_dir}):")
                                with open(filepath, "r", encoding="utf-8") as f:
                                    content = f.read()
                                    print(content)
    
    # 查看recruit_logs
    recruit_log_path = os.path.join(log_root, "recruit_logs")
    if os.path.exists(recruit_log_path):
        print(f"\n📂 招聘日志:")
        print("-" * 80)
        
        for filename in os.listdir(recruit_log_path):
            filepath = os.path.join(recruit_log_path, filename)
            if os.path.isfile(filepath):
                print(f"\n📄 {filename}:")
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)
    
    # 查看dialog_logs
    dialog_log_path = os.path.join(log_root, "log_dialog")
    if os.path.exists(dialog_log_path):
        print(f"\n📂 对话日志:")
        print("-" * 80)
        
        for date_dir in os.listdir(dialog_log_path):
            date_path = os.path.join(dialog_log_path, date_dir)
            if os.path.isdir(date_path):
                for filename in os.listdir(date_path):
                    filepath = os.path.join(date_path, filename)
                    if os.path.isfile(filepath):
                        print(f"\n📄 {filename}:")
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            print(content)
    
    print("\n" + "=" * 80)
    print("✅ 完整测试流程完成！")
    print("=" * 80)

def main():
    """主测试流程"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "🧠 张三的AI面试完整测试流程 🧠" + " " * 15 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    job_name = "数据分析师"
    
    # 1. 初始化数据库
    init_test_database()
    
    # 2. 保存简历记录
    resume_id, detail_data = save_zhang_san_resume(job_name)
    
    # 3. 创建面试链接
    interview_url, token = create_zhang_san_interview(resume_id, detail_data)
    if not token:
        return
    
    # 4. 生成面试题目
    questions = generate_zhang_san_questions(token, job_name)
    
    # 5. 模拟完成面试
    all_answers = simulate_zhang_san_answers(token, questions, job_name)
    
    # 6. 面试评分
    score_zhang_san_interview(token, all_answers, job_name)
    
    # 7. 展示所有日志
    show_logs()

if __name__ == "__main__":
    main()

