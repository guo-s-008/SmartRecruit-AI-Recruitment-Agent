
@echo off
echo ========================================
echo   智聘未来 · AI 全流程智能招聘系统
echo   Windows一键启动脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python检查通过
echo.

echo [2/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️ 依赖安装可能有问题，但继续尝试启动...
)
echo ✅ 依赖处理完成
echo.

echo [3/4] 检查配置文件...
if not exist "04_数据文件\.env" (
    echo ⚠️ 未找到.env文件，从.env.example复制...
    copy "04_数据文件\.env.example" "04_数据文件\.env"
    echo ✅ 配置文件已创建，请编辑 04_数据文件\.env 填入您的配置
)
echo ✅ 配置检查完成
echo.

echo [4/4] 初始化测试数据...
cd 03_项目代码
python add_test_data.py
cd ..
echo.

echo ========================================
echo   🎉 准备完成！正在启动应用...
echo ========================================
echo.
echo 🌐 应用将在浏览器中打开
echo 📖 访问地址: http://localhost:8501
echo.
echo 按 Ctrl+C 可停止应用
echo.

streamlit run 03_项目代码/pages/main/chat_main.py

pause

