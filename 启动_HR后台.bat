@echo off
chcp 65001 >nul
echo ========================================
echo   智聘未来 - HR后台管理系统
echo   Windows一键启动脚本
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python！
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo ✅ Python环境检查通过
echo.

echo [2/5] 安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️ 依赖安装有警告，但继续尝试启动
)
echo ✅ 依赖处理完成
echo.

echo [3/5] 检查配置文件...
if not exist "04_数据文件\.env" (
    echo ⚠️ 未找到配置文件，从模板复制
    copy "04_数据文件\.env.example" "04_数据文件\.env"
    echo ✅ 配置文件已创建
) else (
    echo ✅ 配置文件已存在
)
echo.

echo [4/5] 初始化数据库...
cd 03_项目代码
python add_test_data.py
cd ..
echo ✅ 数据库初始化完成
echo.

echo [5/5] 启动HR后台...
echo.
echo ========================================
echo   🎉 HR后台即将启动！
echo ========================================
echo.
echo 📖 访问地址：http://localhost:8501
echo.
echo ⏹️  按 Ctrl+C 停止应用
echo.

streamlit run 03_项目代码/pages/hr/hr_dashboard.py

pause