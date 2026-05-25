#!/bin/bash

echo "========================================"
echo "  智聘未来 - AI全流程智能招聘系统"
echo "  Mac/Linux一键启动脚本"
echo "========================================"
echo ""

echo "[1/5] 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo "❌ 未找到Python！"
    echo ""
    echo "请先安装Python 3.8或更高版本"
    echo "下载地址：https://www.python.org/downloads/"
    echo ""
    exit 1
fi
$PYTHON_CMD --version
echo "✅ Python环境检查通过"
echo ""

echo "[2/5] 安装项目依赖..."
$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "⚠️ 依赖安装有警告，但继续尝试启动"
fi
echo "✅ 依赖处理完成"
echo ""

echo "[3/5] 检查配置文件..."
if [ ! -f "04_数据文件/.env" ]; then
    echo "⚠️ 未找到配置文件，从模板复制"
    cp "04_数据文件/.env.example" "04_数据文件/.env"
    echo "✅ 配置文件已创建"
else
    echo "✅ 配置文件已存在"
fi
echo ""

echo "[4/5] 初始化数据库..."
cd "03_项目代码"
$PYTHON_CMD add_test_data.py
cd ..
echo "✅ 数据库初始化完成"
echo ""

echo "[5/5] 启动应用..."
echo ""
echo "========================================"
echo "  🎉 应用即将启动！"
echo "========================================"
echo ""
echo "📖 访问地址：http://localhost:8501"
echo ""
echo "⏹️  按 Ctrl+C 停止应用"
echo ""

streamlit run "03_项目代码/pages/main/chat_main.py"