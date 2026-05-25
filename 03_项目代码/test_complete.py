
"""
完整的系统测试脚本
"""
import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=" * 80)
print("🚀 智聘未来 - 完整系统测试")
print("=" * 80)
print()

# ==========================================
# 测试1: 配置检查
# ==========================================
print("📋 测试1: 配置检查")
print("-" * 60)
try:
    from config import USE_SQLITE, API_CONFIG
    print(f"  ✅ 配置文件加载成功")
    print(f"  ✅ 数据库模式: {'SQLite' if USE_SQLITE else 'MySQL'}")
    print(f"  ✅ API Key已配置: {'是' if API_CONFIG.get('key') else '否'}")
    
except Exception as e:
    print(f"  ❌ 配置检查失败: {e}")
    sys.exit(1)

print()

# ==========================================
# 测试2: 依赖检查
# ==========================================
print("📋 测试2: 依赖检查")
print("-" * 60)
dependencies = [
    ("streamlit", "Web框架"),
    ("pymysql", "MySQL驱动"),
    ("pandas", "数据处理"),
    ("openpyxl", "Excel处理"),
    ("requests", "HTTP请求"),
    ("python_docx", "Word文档"),
    ("PyPDF2", "PDF处理")
]

for dep_name, desc in dependencies:
    try:
        __import__(dep_name.replace("-", "_"))
        print(f"  ✅ {dep_name:15} - {desc}")
    except ImportError:
        print(f"  ❌ {dep_name:15} - 未安装")

print()

# ==========================================
# 测试3: 数据库连接和数据
# ==========================================
print("📋 测试3: 数据库连接和数据")
print("-" * 60)
try:
    from database import (
        init_tables,
        get_all_jobs,
        get_all_talents
    )
    
    # 初始化表
    print("  🔄 初始化数据库表...")
    init_tables()
    print("  ✅ 数据库表初始化成功")
    
    # 检查数据
    jobs = get_all_jobs()
    talents = get_all_talents()
    
    print(f"  ✅ 岗位总数: {len(jobs)}")
    print(f"  ✅ 人才总数: {len(talents)}")
    
    if jobs:
        print(f"  📋 岗位示例:")
        for i, job in enumerate(jobs[:3]):
            print(f"     {i+1}. {job.get('job_name', 'N/A')}")
    
    if talents:
        print(f"  📋 人才示例:")
        for i, talent in enumerate(talents[:3]):
            print(f"     {i+1}. {talent.get('name', 'N/A')} - {talent.get('education', 'N/A')}")
    
except Exception as e:
    print(f"  ❌ 数据库测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ==========================================
# 测试4: AI模块
# ==========================================
print("📋 测试4: AI模块导入")
print("-" * 60)
try:
    from ai_scorer import call_llm, analyze_candidates_comparison
    print("  ✅ AI模块导入成功")
except Exception as e:
    print(f"  ⚠️ AI模块导入: {e} (API可能未配置)")

print()

# ==========================================
# 测试5: 页面模块
# ==========================================
print("📋 测试5: 页面模块导入")
print("-" * 60)

page_modules = [
    ("主应用", "pages.main.chat_main"),
    ("HR后台", "pages.hr.hr_dashboard"),
    ("候选人对比", "pages.hr.candidate_comparison"),
    ("自动化筛选", "pages.hr.auto_filter"),
    ("面试页面", "pages.interview_page")
]

for name, module_path in page_modules:
    try:
        # 只是检查文件是否存在和导入路径
        module_file = os.path.join(current_dir, module_path.replace(".", "/") + ".py")
        if os.path.exists(module_file):
            print(f"  ✅ {name}")
        else:
            print(f"  ⚠️ {name} (文件不存在)")
    except Exception as e:
        print(f"  ❌ {name}: {e}")

print()

# ==========================================
# 测试6: 数据文件检查
# ==========================================
print("📋 测试6: 数据文件检查")
print("-" * 60)
data_dir = os.path.join(os.path.dirname(current_dir), "04_数据文件", "job_jd")
if os.path.exists(data_dir):
    jd_files = [f for f in os.listdir(data_dir) if f.endswith("_jd.txt")]
    scoring_files = [f for f in os.listdir(data_dir) if f.endswith("_scoring.txt")]
    print(f"  ✅ 岗位JD文件: {len(jd_files)}")
    print(f"  ✅ 评分标准文件: {len(scoring_files)}")
else:
    print("  ⚠️ 数据文件目录不存在")

print()

# ==========================================
# 测试总结
# ==========================================
print("=" * 80)
print("🎉 测试完成总结")
print("=" * 80)
print()
print("📊 系统状态:")
print(f"  ✅ 数据库模式: {'SQLite' if USE_SQLITE else 'MySQL'}")
print(f"  ✅ 岗位数据: {len(jobs)} 条")
print(f"  ✅ 人才数据: {len(talents)} 条")
print()
print("🌐 访问地址:")
print("  主应用: http://localhost:8501")
print("  HR后台: http://localhost:8503")
print()
print("🚀 下一步:")
print("  1. 启动主应用")
print("  2. 启动HR后台")
print("  3. 在浏览器中访问测试")
print()

