"""
添加测试数据到人才库
"""
import sys
import os
from datetime import datetime

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database_sqlite import add_talent_to_pool, query_jobs_from_db, get_db_connection

# 测试人才数据
TEST_TALENTS = [
    {
        "name": "李明",
        "gender": "男",
        "age": "26",
        "education": "硕士",
        "major": "计算机科学与技术",
        "city": "北京",
        "email": "liming@example.com",
        "phone": "13800001111",
        "skills": "Python,Java,机器学习,深度学习,数据分析,TensorFlow",
        "experience": "3年经验，曾在字节跳动担任算法工程师",
        "resume_text": "李明，硕士学历，3年算法工程师经验...",
        "tags": "算法工程师,AI,机器学习",
        "source": "简历投递"
    },
    {
        "name": "王芳",
        "gender": "女",
        "age": "24",
        "education": "本科",
        "major": "软件工程",
        "city": "上海",
        "email": "wangfang@example.com",
        "phone": "13800002222",
        "skills": "Python,SQL,数据分析,Pandas,NumPy",
        "experience": "2年经验，数据分析师",
        "resume_text": "王芳，本科学历，2年数据分析经验...",
        "tags": "数据分析师,数据分析,Python",
        "source": "简历投递"
    },
    {
        "name": "张伟",
        "gender": "男",
        "age": "28",
        "education": "博士",
        "major": "人工智能",
        "city": "深圳",
        "email": "zhangwei@example.com",
        "phone": "13800003333",
        "skills": "Python,Go,大数据,Hadoop,Spark,算法",
        "experience": "5年经验，曾在阿里巴巴担任高级工程师",
        "resume_text": "张伟，博士学历，5年大厂经验...",
        "tags": "高级工程师,大数据,架构师",
        "source": "猎头推荐"
    },
    {
        "name": "刘洋",
        "gender": "男",
        "age": "25",
        "education": "硕士",
        "major": "数据科学",
        "city": "杭州",
        "email": "liuyang@example.com",
        "phone": "13800004444",
        "skills": "Python,R,SQL,机器学习,统计分析",
        "experience": "1年经验，数据科学工程师",
        "resume_text": "刘洋，硕士学历，1年数据科学经验...",
        "tags": "数据科学,机器学习,统计",
        "source": "简历投递"
    },
    {
        "name": "陈静",
        "gender": "女",
        "age": "27",
        "education": "硕士",
        "major": "计算机应用",
        "city": "北京",
        "email": "chenjing@example.com",
        "phone": "13800005555",
        "skills": "Java,Python,数据库,微服务,Spring Boot",
        "experience": "4年经验，后端开发工程师",
        "resume_text": "陈静，硕士学历，4年后端开发经验...",
        "tags": "后端开发,Java,全栈",
        "source": "简历投递"
    },
    {
        "name": "赵磊",
        "gender": "男",
        "age": "29",
        "education": "本科",
        "major": "信息安全",
        "city": "上海",
        "email": "zhaolei@example.com",
        "phone": "13800006666",
        "skills": "Python,安全测试,渗透测试,网络工程",
        "experience": "6年经验，安全工程师",
        "resume_text": "赵磊，本科学历，6年安全领域经验...",
        "tags": "安全工程师,渗透测试",
        "source": "内部推荐"
    },
    {
        "name": "周婷",
        "gender": "女",
        "age": "23",
        "education": "本科",
        "major": "统计学",
        "city": "北京",
        "email": "zhouting@example.com",
        "phone": "13800007777",
        "skills": "R,Python,SQL,数据可视化,Tableau",
        "experience": "1年经验，数据分析师",
        "resume_text": "周婷，本科学历，统计学背景...",
        "tags": "数据分析师,可视化,BI",
        "source": "简历投递"
    },
    {
        "name": "吴强",
        "gender": "男",
        "age": "30",
        "education": "博士",
        "major": "机器学习",
        "city": "深圳",
        "email": "wuqiang@example.com",
        "phone": "13800008888",
        "skills": "Python,深度学习,NLP,推荐系统,算法",
        "experience": "7年经验，算法专家",
        "resume_text": "吴强，博士学历，7年AI领域经验...",
        "tags": "算法专家,NLP,推荐系统",
        "source": "猎头推荐"
    }
]

# 测试岗位数据
TEST_JOBS = [
    {
        "job_name": "AI算法工程师",
        "jd_content": "负责AI算法研发，要求：\n1. 硕士及以上学历\n2. 精通Python\n3. 熟悉机器学习、深度学习\n4. 有NLP或推荐系统经验优先",
        "education": "硕士",
        "city": "北京",
        "is_intern": 0,
        "hiring_count": 2,
        "scoring_criteria": "1. 技术能力 40%\n2. 项目经验 30%\n3. 学历背景 20%\n4. 沟通能力 10%"
    },
    {
        "job_name": "数据分析师",
        "jd_content": "负责数据分析工作，要求：\n1. 本科及以上学历\n2. 熟练使用SQL和Python\n3. 有数据分析经验\n4. 熟悉可视化工具",
        "education": "本科",
        "city": "上海",
        "is_intern": 0,
        "hiring_count": 3,
        "scoring_criteria": "1. 分析能力 35%\n2. 工具使用 30%\n3. 业务理解 25%\n4. 报告能力 10%"
    },
    {
        "job_name": "大数据开发工程师",
        "jd_content": "负责大数据平台开发，要求：\n1. 本科及以上学历\n2. 熟悉Hadoop、Spark\n3. 有大数据处理经验\n4. 熟悉Java或Python",
        "education": "本科",
        "city": "深圳",
        "is_intern": 0,
        "hiring_count": 2,
        "scoring_criteria": "1. 技术能力 45%\n2. 经验匹配 30%\n3. 学历背景 15%\n4. 团队协作 10%"
    }
]

def add_test_jobs():
    """添加测试岗位"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for job in TEST_JOBS:
        try:
            cursor.execute('''
                INSERT INTO job_positions 
                (job_name, jd_content, education, city, is_intern, hiring_count, scoring_criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['job_name'],
                job['jd_content'],
                job['education'],
                job['city'],
                job['is_intern'],
                job['hiring_count'],
                job['scoring_criteria']
            ))
            print(f"✅ 岗位已添加：{job['job_name']}")
        except Exception as e:
            print(f"❌ 添加岗位失败：{job['job_name']} - {e}")
    
    conn.commit()
    conn.close()

def add_test_talents():
    """添加测试人才"""
    for talent in TEST_TALENTS:
        try:
            add_talent_to_pool(talent)
            print(f"✅ 人才已添加：{talent['name']}")
        except Exception as e:
            print(f"❌ 添加人才失败：{talent['name']} - {e}")

def main():
    print("=" * 80)
    print("📦 添加测试数据")
    print("=" * 80)
    
    print("\n1️⃣ 添加测试岗位...")
    add_test_jobs()
    
    print("\n2️⃣ 添加测试人才...")
    add_test_talents()
    
    print("\n" + "=" * 80)
    print("✅ 测试数据添加完成！")
    print("=" * 80)
    
    # 统计
    talents = []
    for t in TEST_TALENTS:
        talents.append(t['name'])
    
    jobs = query_jobs_from_db()
    
    print(f"\n📊 数据统计：")
    print(f"  - 人才总数：{len(talents)}")
    print(f"  - 岗位总数：{len(jobs)}")
    print(f"\n📋 人才列表：")
    for name in talents:
        print(f"  • {name}")
    print(f"\n📋 岗位列表：")
    for job in jobs:
        print(f"  • {job}")

if __name__ == "__main__":
    main()
