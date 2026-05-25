
"""
初始化MySQL数据库测试数据
"""
import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database import (
    init_tables,
    add_job_to_db,
    add_talent_to_pool,
    get_all_jobs,
    get_all_talents,
    query_jobs_from_db
)
from config import JD_FOLDER

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

def load_jd_from_file(job_name):
    """从文件加载JD和评分标准"""
    jd_content = ""
    scoring_criteria = ""
    
    # 尝试从文件读取
    jd_file = os.path.join(JD_FOLDER, f"{job_name}_jd.txt")
    scoring_file = os.path.join(JD_FOLDER, f"{job_name}_scoring.txt")
    
    if os.path.exists(jd_file):
        with open(jd_file, 'r', encoding='utf-8') as f:
            jd_content = f.read()
    
    if os.path.exists(scoring_file):
        with open(scoring_file, 'r', encoding='utf-8') as f:
            scoring_criteria = f.read()
    
    return jd_content, scoring_criteria

def get_all_jobs_from_files():
    """从文件目录获取所有岗位"""
    jobs = []
    
    if not os.path.exists(JD_FOLDER):
        print(f"⚠️ JD文件夹不存在：{JD_FOLDER}")
        return jobs
    
    # 扫描目录下的所有JD文件
    files = os.listdir(JD_FOLDER)
    job_names = set()
    
    for file in files:
        if file.endswith('_jd.txt'):
            job_name = file.replace('_jd.txt', '')
            job_names.add(job_name)
    
    # 为每个岗位创建数据
    for job_name in job_names:
        jd_content, scoring_criteria = load_jd_from_file(job_name)
        
        # 默认数据
        job_data = {
            "job_name": job_name,
            "jd_content": jd_content or f"{job_name}岗位描述",
            "scoring_criteria": scoring_criteria or "1. 技术能力 40%\n2. 项目经验 30%\n3. 学历背景 20%\n4. 沟通能力 10%",
            "education": "本科",
            "city": "北京",
            "is_intern": 0,
            "hiring_count": 1,
            "is_open": 1
        }
        jobs.append(job_data)
    
    return jobs

def add_test_jobs():
    """添加测试岗位"""
    # 首先从文件加载岗位
    jobs_from_files = get_all_jobs_from_files()
    
    if jobs_from_files:
        print(f"📄 从文件加载了 {len(jobs_from_files)} 个岗位")
        for job in jobs_from_files:
            try:
                add_job_to_db(job)
                print(f"✅ 岗位已添加：{job['job_name']}")
            except Exception as e:
                print(f"❌ 添加岗位失败：{job['job_name']} - {e}")
    else:
        print("⚠️ 未找到文件中的岗位，添加默认测试岗位")
        # 默认测试岗位
        default_jobs = [
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
        for job in default_jobs:
            try:
                add_job_to_db(job)
                print(f"✅ 岗位已添加：{job['job_name']}")
            except Exception as e:
                print(f"❌ 添加岗位失败：{job['job_name']} - {e}")

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
    print("🗄️ 初始化MySQL数据库测试数据")
    print("=" * 80)
    
    try:
        # 1. 初始化数据库表
        print("\n1️⃣ 初始化数据库表...")
        init_tables()
        
        # 2. 添加测试岗位
        print("\n2️⃣ 添加测试岗位...")
        add_test_jobs()
        
        # 3. 添加测试人才
        print("\n3️⃣ 添加测试人才...")
        add_test_talents()
        
        print("\n" + "=" * 80)
        print("✅ 测试数据初始化完成！")
        print("=" * 80)
        
        # 统计
        jobs = get_all_jobs()
        talents = get_all_talents()
        
        print(f"\n📊 数据统计：")
        print(f"  - 岗位总数：{len(jobs)}")
        print(f"  - 人才总数：{len(talents)}")
        
        print(f"\n📋 岗位列表：")
        for job in jobs:
            status = "✅开放" if job.get('is_open') else "❌关闭"
            print(f"  • {job['job_name']} ({job['city']}) - {status}")
        
        print(f"\n📋 人才列表：")
        for talent in talents:
            status = "✅活跃" if talent.get('status') == 'active' else "❌非活跃"
            print(f"  • {talent['name']} - {talent['email']} - {status}")
            
    except Exception as e:
        print(f"\n❌ 初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
