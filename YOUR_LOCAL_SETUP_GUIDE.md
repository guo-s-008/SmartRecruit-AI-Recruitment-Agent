
# 💻 在您自己的电脑上部署项目

## 📋 说明

刚才我是在云端Linux环境中为您演示的。现在这篇指南将帮您把项目部署到**您自己的本地电脑**上！

---

## 🚀 本地部署步骤（在您的电脑上）

### 第一步：下载项目代码

#### 方式一：如果这个项目是在Git仓库中
```bash
# 克隆项目
cd 您想存放项目的目录
git clone <您的仓库地址>
cd <项目目录>
```

#### 方式二：如果只有文件
直接把整个 `/workspace/` 文件夹复制到您的电脑上

---

### 第二步：安装Python

确保您的电脑上安装了 Python 3.8 或更高版本

```bash
# 检查Python版本
python --version
# 或者
python3 --version
```

下载地址：https://www.python.org/downloads/

---

### 第三步：安装依赖

在项目根目录下打开终端/命令提示符：

```bash
# 进入项目目录
cd <您的项目目录>

# 安装依赖
pip install -r requirements.txt
```

---

### 第四步：配置环境变量

复制 `04_数据文件/.env.example` 为 `04_数据文件/.env`，然后填入您的配置：

```env
# 数据库配置（先使用SQLite，最简单）
# 不需要配置MySQL也能运行！

# 阿里云百炼 API 配置
API_KEY=sk-b377a05698164c1b9997b3ed701a1b62
API_URL=https://dashscope-api.cn-beijing.aliyuncs.com/api/text/v1/chat
API_MODEL=qwen-turbo

# 邮件配置（可选，不配置邮件功能会用日志代替）
MAIL_SENDER=您的邮箱@qq.com
MAIL_PASSWORD=您的邮箱授权码
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
HR_EMAIL=hr@example.com

# 应用配置
APP_BASE_URL=http://localhost:8501
```

---

### 第五步：确认使用SQLite（最简单！）

**不需要安装MySQL也能运行！** 我已经为您配置好SQLite模式：

在 `03_项目代码/config.py` 中确认：
```python
USE_SQLITE = True  # 保持这个设置
```

这样就不需要安装MySQL数据库了！

---

### 第六步：初始化测试数据

```bash
cd 03_项目代码
python add_test_data.py
```

---

### 第七步：启动应用！

```bash
# 返回项目根目录
cd ..

# 启动主应用
streamlit run 03_项目代码/pages/main/chat_main.py
```

然后浏览器会自动打开，或者手动访问：
**http://localhost:8501**

---

## 📁 项目文件结构（在您电脑上应该这样组织：
```
您的项目目录/
├── 01_简历投递收件箱/
├── 02_已处理简历/
├── 03_项目代码/
├── 04_数据文件/
├── 05_ppt素材/
├── 06_视频素材/
├── 07_系统日志/
├── requirements.txt
└── readme.md
```

---

## 🎯 快速启动命令（在您电脑上）

### Windows用户（使用CMD或PowerShell）：
```cmd
# 1. 进入项目目录
cd C:\您的项目目录

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据
cd 03_项目代码
python add_test_data.py
cd ..

# 4. 启动应用
streamlit run 03_项目代码/pages/main/chat_main.py
```

### Mac/Linux用户：
```bash
# 1. 进入项目目录
cd ~/您的项目目录

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据
cd 03_项目代码
python add_test_data.py
cd ..

# 4. 启动应用
streamlit run 03_项目代码/pages/main/chat_main.py
```

---

## 🔧 需要我帮您做什么？

我可以帮您：
1. 📦 打包项目文件供您下载
2. 📝 创建一键启动脚本
3. 🛠️ 根据您的操作系统调整配置
4. 🐛 解决部署过程中的任何问题

**请告诉我您需要什么帮助！