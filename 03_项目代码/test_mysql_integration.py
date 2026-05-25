
"""
测试MySQL集成是否正常工作
"""
import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=" * 80)
print("🧪 MySQL集成测试")
print("=" * 80)

# 1. 测试环境配置
print("\n1️⃣  测试环境配置...")
try:
    from config import USE_SQLITE, MYSQL_CONFIG
    print(f"   ✅ 配置加载成功")
    print(f"   • USE_SQLITE: {USE_SQLITE}")
    print(f"   • MySQL配置: {MYSQL_CONFIG}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")
    sys.exit(1)

if USE_SQLITE:
    print("\n⚠️  当前配置使用SQLite，需要切换到MySQL进行测试")
    print("   请修改 config.py 中的 USE_SQLITE = False")
    sys.exit(0)

# 2. 测试MySQL连接
print("\n2️⃣  测试MySQL连接...")
try:
    import pymysql
    from pymysql import Error
    
    # 尝试连接MySQL
    conn = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"]
    )
    print("   ✅ MySQL连接成功")
    
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"   • MySQL版本: {version[0]}")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("   ❌ pymysql模块未安装")
    print("   请运行: pip install pymysql")
    sys.exit(1)
except Error as e:
    print(f"   ❌ MySQL连接失败: {e}")
    print("\n💡 请检查：")
    print("   1. MySQL服务是否已启动")
    print("   2. 配置是否正确（用户名、密码、端口等）")
    print("   3. 数据库是否存在")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ 未知错误: {e}")
    sys.exit(1)

# 3. 测试数据库模块导入
print("\n3️⃣  测试数据库模块...")
try:
    from database import (
        init_tables,
        add_job_to_db,
        add_talent_to_pool,
        get_all_jobs,
        get_all_talents,
        query_jobs_from_db,
        get_jd_from_db
    )
    print("   ✅ 数据库模块导入成功")
except Exception as e:
    print(f"   ❌ 数据库模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 测试初始化表
print("\n4️⃣  测试初始化表...")
try:
    init_tables()
    print("   ✅ 表初始化成功")
except Exception as e:
    print(f"   ❌ 表初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 测试添加岗位
print("\n5️⃣  测试添加岗位...")
try:
    test_job = {
        "job_name": "测试工程师",
        "jd_content": "负责软件测试工作，要求熟悉Python、SQL等",
        "scoring_criteria": "技术能力40%，项目经验30%，学历20%，沟通10%",
        "education": "本科",
        "city": "北京",
        "is_intern": 0,
        "hiring_count": 1,
        "is_open": 1
    }
    job_id = add_job_to_db(test_job)
    print(f"   ✅ 岗位添加成功，ID: {job_id}")
except Exception as e:
    print(f"   ❌ 岗位添加失败: {e}")
    import traceback
    traceback.print_exc()

# 6. 测试查询岗位
print("\n6️⃣  测试查询岗位...")
try:
    jobs = query_jobs_from_db()
    print(f"   ✅ 查询成功，共 {len(jobs)} 个岗位")
    if jobs:
        print(f"   • 岗位列表: {jobs}")
    
    all_jobs = get_all_jobs()
    print(f"   • 完整岗位数据: {len(all_jobs)} 条")
except Exception as e:
    print(f"   ❌ 岗位查询失败: {e}")

# 7. 测试添加人才
print("\n7️⃣  测试添加人才...")
try:
    test_talent = {
        "name": "测试用户",
        "gender": "男",
        "age": "25",
        "education": "本科",
        "major": "计算机科学",
        "city": "北京",
        "email": "test@example.com",
        "phone": "13800138000",
        "skills": "Python, SQL, 软件测试",
        "experience": "2年测试经验",
        "resume_text": "这是测试简历内容...",
        "tags": "测试, 质量保证",
        "source": "测试"
    }
    talent_id = add_talent_to_pool(test_talent)
    print(f"   ✅ 人才添加成功，ID: {talent_id}")
except Exception as e:
    print(f"   ❌ 人才添加失败: {e}")
    import traceback
    traceback.print_exc()

# 8. 测试查询人才
print("\n8️⃣  测试查询人才...")
try:
    talents = get_all_talents()
    print(f"   ✅ 查询成功，共 {len(talents)} 个人才")
    if talents:
        print(f"   • 人才列表: {[t['name'] for t in talents]}")
except Exception as e:
    print(f"   ❌ 人才查询失败: {e}")

print("\n" + "=" * 80)
print("🎉 MySQL集成测试完成！")
print("=" * 80)
print("\n💡 下一步建议：")
print("   1. 运行 init_mysql_test_data.py 添加完整测试数据")
print("   2. 启动 streamlit 应用进行完整测试")
print("   3. 访问 HR 后台进行增删改查测试")
