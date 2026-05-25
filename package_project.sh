#!/bin/bash
# 项目打包脚本

echo "========================================="
echo "  📦 项目打包脚本"
echo "========================================="

# 创建临时目录用于打包
TEMP_DIR="/tmp/project_package"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 复制项目文件（排除不需要的文件）
echo "📁 复制项目文件..."

# 复制项目代码
cp -r "03_项目代码" "$TEMP_DIR/"
# 排除测试脚本
rm -f "$TEMP_DIR/03_项目代码/test_*.py"
rm -f "$TEMP_DIR/03_项目代码/quick_start.py"

# 复制数据文件
cp -r "04_数据文件" "$TEMP_DIR/"

# 复制根目录文件
cp requirements.txt "$TEMP_DIR/"
cp readme.md "$TEMP_DIR/"
cp README_FIRST.md "$TEMP_DIR/"
cp LOCAL_DEPLOYMENT.md "$TEMP_DIR/"
cp YOUR_LOCAL_SETUP_GUIDE.md "$TEMP_DIR/"
cp COMPLETE_TEST_REPORT.md "$TEMP_DIR/"
cp start_windows.bat "$TEMP_DIR/"
cp start_mac_linux.sh "$TEMP_DIR/"

# 创建必要的目录
mkdir -p "$TEMP_DIR/01_简历投递收件箱"
mkdir -p "$TEMP_DIR/02_已处理简历"
mkdir -p "$TEMP_DIR/05_ppt素材"
mkdir -p "$TEMP_DIR/06_视频素材"
mkdir -p "$TEMP_DIR/07_系统日志"

# 创建gitkeep文件
touch "$TEMP_DIR/01_简历投递收件箱/.gitkeep"
touch "$TEMP_DIR/02_已处理简历/.gitkeep"
touch "$TEMP_DIR/05_ppt素材/.gitkeep"
touch "$TEMP_DIR/06_视频素材/.gitkeep"
touch "$TEMP_DIR/07_系统日志/.gitkeep"

# 创建.gitignore
cat > "$TEMP_DIR/.gitignore" << 'EOF'
# 日志文件
*.log
07_系统日志/

# 简历文件
01_简历投递收件箱/
02_已处理简历/

# 临时文件
*.pyc
__pycache__/
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# 数据库
*.db
*.sqlite

# 环境变量（不要上传.env）
.env

# Mac
.DS_Store

# 视频素材
06_视频素材/

# PPT素材
05_ppt素材/
EOF

# 创建.env示例文件
cat > "$TEMP_DIR/04_数据文件/.env.example" << 'EOF'
# 数据库配置（使用SQLite，无需修改）
USE_SQLITE=True

# MySQL配置（可选，如果要使用MySQL）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=recruitment
MYSQL_CHARSET=utf8mb4

# 阿里云百炼 API 配置
API_KEY=sk-your-api-key
API_URL=https://dashscope-api.cn-beijing.aliyuncs.com/api/text/v1/chat
API_MODEL=qwen-turbo

# 邮件配置
MAIL_SENDER=your_email@qq.com
MAIL_PASSWORD=your_email_password
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
HR_EMAIL=hr@example.com

# 应用配置
APP_BASE_URL=http://localhost:8501
EOF

echo "✅ 文件复制完成"

# 创建zip包
echo "📦 创建ZIP压缩包..."
cd /tmp
zip -r "zhipin_future_project.zip" "project_package"
ZIP_PATH="/tmp/zhipin_future_project.zip"

echo "========================================="
echo "  ✅ 打包完成！"
echo "========================================="
echo ""
echo "📁 压缩包位置："
echo "   $ZIP_PATH"
echo ""
echo "📊 包大小："
ls -lh "$ZIP_PATH"
echo ""
echo "🎯 下一步："
echo "   1. 下载压缩包到您的电脑"
echo "   2. 解压到您的项目目录"
echo "   3. 运行启动脚本（Windows: start_windows.bat）"
echo ""

