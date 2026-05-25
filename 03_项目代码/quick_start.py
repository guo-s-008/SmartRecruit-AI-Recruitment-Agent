
"""
快速启动脚本 - 初始化数据并准备运行
"""
import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=" * 80)
print("🚀 智聘未来 · AI 全流程智能招聘系统 - 快速启动")
print("=" * 80)

# 检查配置
from config import USE_SQLITE, API_CONFIG, BASE_DIR
print(f"\n✅ 配置检查：")
print(f"  • 数据库模式：{'SQLite（无需服务器）' if USE_SQLITE else 'MySQL'}")
print(f"  • API Key配置：{'已配置' if API_CONFIG['key'] and API_CONFIG['key'] != 'your_api_key_here' else '未配置'}")
print(f"  • 项目目录：{BASE_DIR}")

# 初始化数据
print(f"\n📋 初始化测试数据...")
try:
    from add_test_data import main as init_test_data
    init_test_data()
    print("✅ 测试数据初始化成功！")
except Exception as e:
    print(f"⚠️ 测试数据初始化：{e}")

print("\n" + "=" * 80)
print("🎉 准备完成！现在可以启动应用了")
print("=" * 80)
print("\n📖 使用说明：")
print("  1. 启动主应用：")
print("     streamlit run 03_项目代码/pages/main/chat_main.py")
print("\n  2. 启动HR后台：")
print("     streamlit run 03_项目代码/pages/hr/hr_dashboard.py")
print("\n  3. 或者从项目根目录启动：")
print("     cd /workspace")
print("     streamlit run 03_项目代码/pages/main/chat_main.py")
print("\n" + "=" * 80)

