#!/bin/bash
# 重新打包项目

echo "========================================="
echo "  📦 重新打包项目"
echo "========================================="

# 删除旧的临时目录
rm -rf /tmp/project_package /tmp/zhipin_future_project.zip

# 创建临时目录
mkdir -p /tmp/project_package

# 复制所有项目文件
echo "📁 复制文件..."

# 复制项目核心目录
cp -r "03_项目代码" /tmp/project_package/
cp -r "04_数据文件" /tmp/project_package/

# 创建必要的目录
mkdir -p /tmp/project_package/01_简历投递收件箱
mkdir -p /tmp/project_package/02_已处理简历
mkdir -p /tmp/project_package/05_ppt素材
mkdir -p /tmp/project_package/06_视频素材
mkdir -p /tmp/project_package/07_系统日志

# 复制根目录文件
cp requirements.txt /tmp/project_package/
cp readme.md /tmp/project_package/
cp README_FIRST.md /tmp/project_package/
cp LOCAL_DEPLOYMENT.md /tmp/project_package/
cp YOUR_LOCAL_SETUP_GUIDE.md /tmp/project_package/
cp COMPLETE_TEST_REPORT.md /tmp/project_package/
cp start_simple.bat /tmp/project_package/
cp start_windows.bat /tmp/project_package/
cp start_mac_linux.sh /tmp/project_package/
cp QUICK_START_WINDOWS.md /tmp/project_package/

# 创建gitkeep
touch /tmp/project_package/01_简历投递收件箱/.gitkeep
touch /tmp/project_package/02_已处理简历/.gitkeep
touch /tmp/project_package/05_ppt素材/.gitkeep
touch /tmp/project_package/06_视频素材/.gitkeep
touch /tmp/project_package/07_系统日志/.gitkeep

# 创建.gitignore
cat > /tmp/project_package/.gitignore << 'EOF'
*.log
*.db
07_系统日志/
__pycache__/
.env
.DS_Store
EOF

# 创建.env.example
cat > /tmp/project_package/04_数据文件/.env.example << 'EOF'
USE_SQLITE=True
API_KEY=sk-b377a05698164c1b9997b3ed701a1b62
API_URL=https://dashscope-api.cn-beijing.aliyuncs.com/api/text/v1/chat
API_MODEL=qwen-turbo
MAIL_SENDER=1962029495@qq.com
MAIL_PASSWORD=jbmxgrltpcumdgbb
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
HR_EMAIL=q17877881463qq@163.com
APP_BASE_URL=http://localhost:8501
EOF

# 复制.env作为初始文件
cp 04_数据文件/.env /tmp/project_package/04_数据文件/.env

# 创建zip包（直接打包文件，不要外层project_package）
echo "📦 创建ZIP..."
cd /tmp/project_package
zip -r ../zhipin_future_project.zip ./*
cd ..

# 复制到workspace
cp /tmp/zhipin_future_project.zip /workspace/

echo "========================================="
echo "  ✅ 重新打包完成！"
echo "========================================="
echo "文件位置：/workspace/zhipin_future_project.zip"
ls -lh /workspace/zhipin_future_project.zip
echo ""

