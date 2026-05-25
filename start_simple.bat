@echo off
chcp 65001 >nul
echo ========================================
echo   Zhipin Future - Startup
echo ========================================
echo.

echo [1] Check Python...
py --version
if errorlevel 1 (
    echo Error: Python not found!
    pause
    exit /b 1
)
echo OK: Python OK
echo.

echo [2] Install dependencies...
pip install -r requirements.txt
echo OK: Dependencies installed
echo.

echo [3] Initialize test data...
cd 03_项目代码
py add_test_data.py
cd ..
echo OK: Data initialized
echo.

echo ========================================
echo   Starting app...
echo ========================================
echo.

echo Open browser at: http://localhost:8501
echo.

streamlit run 03_项目代码/pages/main/chat_main.py

pause

