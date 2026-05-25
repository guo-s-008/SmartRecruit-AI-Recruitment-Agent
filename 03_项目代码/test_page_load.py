"""
测试页面加载脚本
"""
import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=" * 80)
print("🧪 测试HR后台页面加载")
print("=" * 80)

# 测试1：导入HR后台页面
print("\n1️⃣ 测试导入HR后台页面...")
try:
    sys.path.insert(0, os.path.join(current_dir, "pages/hr"))
    import hr_dashboard
    print("✅ HR后台页面导入成功")
except Exception as e:
    print(f"❌ HR后台页面导入失败：{e}")
    import traceback
    traceback.print_exc()

# 测试2：检查数据库连接
print("\n2️⃣ 测试数据库连接...")
try:
    from config import USE_SQLITE
    print(f"   当前数据库模式：{'SQLite' if USE_SQLITE else 'MySQL'}")
    
    if USE_SQLITE:
        from database_sqlite import get_all_talents, get_all_jobs
    else:
        from database import get_all_talents, get_all_jobs
    
    talents = get_all_talents()
    jobs = get_all_jobs()
    
    print(f"✅ 数据库连接成功")
    print(f"   - 人才总数：{len(talents)}")
    print(f"   - 岗位总数：{len(jobs)}")
    
except Exception as e:
    print(f"❌ 数据库连接失败：{e}")
    import traceback
    traceback.print_exc()

# 测试3：检查所有依赖
print("\n3️⃣ 检查依赖...")
dependencies = [
    "streamlit",
    "pandas",
    "pymysql",
    "dotenv"
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - 未安装")

print("\n" + "=" * 80)
print("📋 总结")
print("=" * 80)
print("""
如果所有测试都通过，说明HR后台页面可以正常加载。

启动HR后台的正确方式：
1. 停止当前运行的应用（Ctrl+C）
2. 运行：streamlit run 03_项目代码/pages/hr/hr_dashboard.py
3. 浏览器会自动打开HR后台页面
""")

