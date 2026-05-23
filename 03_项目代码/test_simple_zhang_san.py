
#!/usr/bin/env python3
"""
简化版张三AI面试测试脚本
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database_sqlite import (
    get_db_connection,
    init_tables
)
from log_system import (
    write_interview_log,
    write_email_log,
    write_recruit_log
)
from interview_service_sqlite import MODULE_NAMES

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

# 张三的面试题目（根据简历生成）
ZHANG_SAN_QUESTIONS = {
    "基础知识": [
        {
            "question": "请介绍一下你所学专业的核心课程有哪些？",
            "reference_answer": "计算机科学与技术专业核心课程包括数据结构、算法设计、计算机网络、操作系统、数据库原理、软件工程、机器学习等。",
            "scoring_points": ["课程熟悉程度", "表达清晰"]
        },
        {
            "question": "你掌握的编程语言有哪些？请举例说明项目中如何使用的。",
            "reference_answer": "熟练掌握Python、Java、Go等语言。在字节跳动实习时使用Python和Go开发推荐系统后端接口。",
            "scoring_points": ["技能广度", "实际应用"]
        },
        {
            "question": "数据库的ACID特性是什么？请简要解释。",
            "reference_answer": "ACID指原子性(Atomicity)、一致性(Consistency)、隔离性(Isolation)和持久性(Durability)，是保证数据库事务可靠性的四个特性。",
            "scoring_points": ["概念理解", "解释清晰"]
        }
    ],
    "项目经历": [
        {
            "question": "请详细介绍你开发的校园二手交易平台项目。",
            "reference_answer": "校园二手交易平台是一个完整的后端项目，使用Python + Django框架开发，实现了用户认证、商品发布、交易、消息通知等功能，使用Redis缓存优化性能。",
            "scoring_points": ["项目描述", "技术深度"]
        },
        {
            "question": "在校园二手交易平台项目中，你遇到的最大挑战是什么？如何解决的？",
            "reference_answer": "最大挑战是系统性能问题。解决方案是使用Redis缓存热点数据，QPS提升了5倍。",
            "scoring_points": ["问题分析", "解决方案"]
        },
        {
            "question": "你在校园二手交易平台项目中的角色和具体贡献是什么？",
            "reference_answer": "我是项目的后端负责人，负责架构设计、核心功能开发、性能优化等，包括用户认证、商品发布、交易系统等模块的开发。",
            "scoring_points": ["职责清晰", "贡献量化"]
        }
    ],
    "实习经历": [
        {
            "question": "请介绍你在字节跳动实习期间的主要工作内容。",
            "reference_answer": "在字节跳动实习时，主要负责抖音推荐系统的后端开发，参与微服务接口的设计和实现，使用Python和Go语言开发，优化了API响应时间。",
            "scoring_points": ["工作内容", "成果表现"]
        },
        {
            "question": "在阿里巴巴实习期间，你有哪些收获？",
            "reference_answer": "在阿里巴巴实习期间，学习了大数据处理技术，使用Hadoop和Spark进行数据处理，编写ETL任务处理每天10TB级别数据。",
            "scoring_points": ["技术学习", "成长体会"]
        }
    ],
    "技能实战": [
        {
            "question": "请描述一次你解决技术难题的经历。",
            "reference_answer": "在字节跳动实习时，优化了一个API接口的响应时间，通过分析代码和数据库查询发现性能瓶颈，优化后从300ms降低到150ms。",
            "scoring_points": ["问题描述", "解决思路"]
        },
        {
            "question": "你最擅长的技术领域是什么？为什么？",
            "reference_answer": "我最擅长后端开发和大数据处理，有两个相关的实习经历，还有多个项目实践，这方面经验丰富。",
            "scoring_points": ["技术深度", "实践经验"]
        },
        {
            "question": "如何保证代码质量？你通常会做哪些检查？",
            "reference_answer": "我会做单元测试、代码评审、使用静态分析工具，遵循代码规范，提交代码前进行全面测试。",
            "scoring_points": ["质量意识", "方法论"]
        }
    ],
    "技能进阶实战": [
        {
            "question": "你对未来的技术发展方向有什么规划？",
            "reference_answer": "我希望在人工智能和大数据领域深入发展，特别是大模型应用和推荐系统方向。",
            "scoring_points": ["规划清晰", "可行性"]
        },
        {
            "question": "如果遇到技术瓶颈，你会如何突破？",
            "reference_answer": "遇到技术瓶颈时，我会先查阅官方文档和论文，然后看有没有开源实现，也会向有经验的同事请教，最后通过实验验证方案。",
            "scoring_points": ["学习能力", "解决策略"]
        },
        {
            "question": "你如何看待技术创新与业务需求之间的关系？",
            "reference_answer": "技术创新应该服务于业务需求，但好的技术创新也能创造新的业务场景，两者是相互促进的关系。",
            "scoring_points": ["思考深度", "实际理解"]
        }
    ]
}

# 张三的回答
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
            "question": "请详细介绍你开发的校园二手交易平台项目。",
            "answer": "校园二手交易平台是我最有代表性的项目。作为后端负责人，我负责整个后端系统的架构设计和开发，使用Python + Django框架，实现了用户认证、商品发布、交易、消息通知等功能。"
        },
        {
            "question": "在校园二手交易平台项目中，你遇到的最大挑战是什么？如何解决的？",
            "answer": "最大的挑战是当用户量增加时系统响应变慢。我使用Redis缓存热点数据，QPS提升了5倍，解决了这个问题。"
        },
        {
            "question": "你在校园二手交易平台项目中的角色和具体贡献是什么？",
            "answer": "我是项目的后端负责人，负责架构设计、核心功能开发、性能优化等。我的贡献包括用户认证、商品发布、交易系统等模块。"
        }
    ],
    "实习经历": [
        {
            "question": "请介绍你在字节跳动实习期间的主要工作内容。",
            "answer": "在字节跳动实习时，我主要负责抖音推荐系统的后端开发，参与微服务接口的设计和实现。在阿里巴巴实习时，参与用户行为分析系统开发。"
        },
        {
            "question": "在阿里巴巴实习期间，你有哪些收获？",
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

def init_database():
    """初始化数据库"""
    print("=" * 80)
    print("📊 1. 初始化数据库...")
    print("=" * 80)
    init_tables()
    print("✅ 数据库初始化完成\n")

def save_resume_and_email(job_name="数据分析师"):
    """保存简历记录和邮件日志"""
    print("=" * 80)
    print("📄 2. 保存张三的简历记录...")
    print("=" * 80)
    
    # 保存简历记录
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO resume_record 
           (deliver_time, name, gender, age, education, major, city, target_city, job, score, email, mail_status, result)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "张三", "男", "24", "本科", 
         "计算机科学与技术", "北京", "北京", job_name, 85, 
         "zhangsan@example.com", "成功", "初筛通过")
    )
    resume_id = cursor.lastrowid
    conn.commit()
    
    # 记录招聘日志
    write_recruit_log(
        resume_name="张三简历.pdf",
        job_name=job_name,
        score=85,
        email="zhangsan@example.com",
        mail_status="成功",
        result_status="初筛通过"
    )
    
    print(f"✅ 简历记录已保存，ID: {resume_id}")
    
    # 记录邮件日志
    email_content = f"""
张三：

恭喜你，你的简历已通过初筛！
请在48小时内完成AI面试。

面试链接：http://localhost:8501/interview_page?token=test_token_123

⚠️ 重要提醒：该面试链接最多只能访问3次，超过3次后将失效，请确保网络稳定！

智聘未来 招聘团队
    """
    
    write_email_log(
        candidate_name="张三",
        email="zhangsan@example.com",
        job_name=job_name,
        score=85,
        result="初筛通过",
        applicant_email_content=email_content,
        hr_email_content=f"面试邀请已发送给 张三 (zhangsan@example.com)"
    )
    
    print("✅ 初筛邮件已记录到日志\n")
    return resume_id

def create_interview_url(resume_id, job_name="数据分析师"):
    """创建面试URL记录"""
    print("=" * 80)
    print("🔗 3. 创建面试URL记录...")
    print("=" * 80)
    
    token = "test_token_123456789"
    interview_url = "http://localhost:8501/interview_page?token=" + token
    
    # 保存面试URL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO interview_url 
           (resume_id, url, token, generated_at, request_count, interrupted)
           VALUES (?, ?, ?, ?, 0, 0)""",
        (resume_id, interview_url, token, datetime.now().isoformat())
    )
    url_id = cursor.lastrowid
    
    # 保存面试记录
    cursor.execute(
        """INSERT INTO interview_record 
           (token, email, candidate_name, resume_name, job_name, resume_id, status, created_at, expired_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (token, "zhangsan@example.com", "张三", "张三简历.pdf", 
         job_name, str(resume_id), "pending", 
         datetime.now().isoformat(), 
         (datetime.now()).isoformat())
    )
    conn.commit()
    conn.close()
    
    print(f"✅ 面试URL已创建，ID: {url_id}")
    print(f"✅ 面试链接: {interview_url}")
    print(f"✅ Token: {token}\n")
    
    return token, interview_url

def simulate_interview(token, job_name="数据分析师"):
    """模拟完整面试过程"""
    print("=" * 80)
    print("🧠 4. 生成张三的AI面试题目...")
    print("=" * 80)
    
    # 保存题目到数据库
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for module_name in MODULE_NAMES:
        questions = ZHANG_SAN_QUESTIONS.get(module_name, [])
        questions_json = json.dumps(questions, ensure_ascii=False)
        
        field_name = f"questions_{module_name}"
        cursor.execute(
            f"UPDATE interview_record SET {field_name}=? WHERE token=?",
            (questions_json, token)
        )
        
        print(f"✅ {module_name} 模块题目已保存，共 {len(questions)} 题")
    
    conn.commit()
    
    # 更新URL访问次数
    print("\n" + "=" * 80)
    print("💬 5. 模拟张三访问面试链接（2次）...")
    print("=" * 80)
    
    cursor.execute(
        "UPDATE interview_url SET request_count=2, used_at=? WHERE token=?",
        (datetime.now().isoformat(), token)
    )
    conn.commit()
    
    print("✅ 已模拟访问 2 次，未中断\n")
    
    print("=" * 80)
    print("💬 6. 模拟张三完成全部面试回答...")
    print("=" * 80)
    
    all_answers = []
    for module_name in MODULE_NAMES:
        print(f"\n📋 回答 [{module_name}] 模块...")
        if module_name in ZHANG_SAN_ANSWERS:
            module_questions = ZHANG_SAN_QUESTIONS.get(module_name, [])
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
    
    # 保存答案
    answers_json = json.dumps(all_answers, ensure_ascii=False)
    cursor.execute(
        "UPDATE interview_record SET answers=? WHERE token=?",
        (answers_json, token)
    )
    conn.commit()
    conn.close()
    
    return all_answers

def score_interview(token, job_name="数据分析师"):
    """AI评分并保存日志"""
    print("\n" + "=" * 80)
    print("📊 7. AI为张三面试评分...")
    print("=" * 80)
    
    module_scores = {
        "基础知识": 9.0,
        "项目经历": 9.5,
        "实习经历": 9.2,
        "技能实战": 8.8,
        "技能进阶实战": 8.5
    }
    
    print("\n📝 各模块评分：")
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
    
    # 更新数据库
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE interview_record SET final_score=?, result=?, status='completed' WHERE token=?",
        (total_score, apply_result, token)
    )
    conn.commit()
    conn.close()
    
    print("\n✅ 面试评分完成！")
    print("✅ 面试记录已保存到日志！\n")
    
    return module_scores, total_score, apply_result

def show_all_logs():
    """展示所有生成的日志"""
    print("=" * 80)
    print("📋 8. 完整日志内容展示")
    print("=" * 80)
    
    log_root = os.path.join(current_dir, "..", "07_系统日志")
    
    # 展示面试日志
    print(f"\n📂 面试日志目录结构:")
    interview_log_path = os.path.join(log_root, "interview_logs")
    if os.path.exists(interview_log_path):
        for root, dirs, files in os.walk(interview_log_path):
            level = root.replace(interview_log_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for filename in files:
                filepath = os.path.join(root, filename)
                print(f"{subindent}{filename}")
                
                if "张三" in filepath and "interview_" in filepath and ".json" in filepath:
                    print(f"\n{'='*80}")
                    print(f"📄 {filename} (内容):")
                    print(f"{'='*80}")
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = json.load(f)
                        print(json.dumps(content, ensure_ascii=False, indent=2))
                elif "张三" in filepath and "interview_detail" in filepath:
                    print(f"\n{'='*80}")
                    print(f"📄 {filename} (内容):")
                    print(f"{'='*80}")
                    with open(filepath, "r", encoding="utf-8") as f:
                        print(f.read())
    
    # 展示邮件日志
    print(f"\n\n📂 邮件日志:")
    email_log_path = os.path.join(log_root, "log_email")
    if os.path.exists(email_log_path):
        for date_dir in sorted(os.listdir(email_log_path)):
            date_path = os.path.join(email_log_path, date_dir)
            if os.path.isdir(date_path):
                for status_dir in sorted(os.listdir(date_path)):
                    status_path = os.path.join(date_path, status_dir)
                    if os.path.isdir(status_path):
                        for filename in sorted(os.listdir(status_path)):
                            if "张三" in filename:
                                filepath = os.path.join(status_path, filename)
                                print(f"\n{'='*80}")
                                print(f"📄 {filename} (路径: {date_dir}/{status_dir}):")
                                print(f"{'='*80}")
                                with open(filepath, "r", encoding="utf-8") as f:
                                    print(f.read())
    
    # 展示招聘日志
    print(f"\n\n📂 招聘日志:")
    recruit_log_path = os.path.join(log_root, "recruit_logs")
    if os.path.exists(recruit_log_path):
        for filename in sorted(os.listdir(recruit_log_path)):
            filepath = os.path.join(recruit_log_path, filename)
            if os.path.isfile(filepath):
                print(f"\n{'='*80}")
                print(f"📄 {filename}:")
                print(f"{'='*80}")
                with open(filepath, "r", encoding="utf-8") as f:
                    print(f.read())
    
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
    init_database()
    
    # 2. 保存简历记录
    resume_id = save_resume_and_email(job_name)
    
    # 3. 创建面试URL
    token, interview_url = create_interview_url(resume_id, job_name)
    
    # 4-6. 模拟面试过程
    simulate_interview(token, job_name)
    
    # 7. 评分
    score_interview(token, job_name)
    
    # 8. 展示日志
    show_all_logs()

if __name__ == "__main__":
    main()

