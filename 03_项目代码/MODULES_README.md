
# 智聘未来 AI 招聘系统 - 模块结构说明

## 📁 项目架构

```
03_项目代码/
├── backend/                    # 后端模块
│   ├── __init__.py             # Python包标识
│   ├── config.py              # 统一配置管理
│   ├── utils.py               # 工具函数
│   ├── database.py            # 数据库操作
│   ├── ai_scorer.py           # AI评分模块
│   ├── resume_parser.py       # 简历解析模块
│   ├── email_service.py       # 邮件服务模块
│   ├── excel_service.py       # Excel操作模块
│   ├── interview_service.py   # 面试服务模块
│   └── log_system.py          # 日志系统模块
│
├── pages/                     # 前端页面
│   ├── main/                  # 主应用页面
│   │   ├── app.py             # 校园招聘投递页面
│   │   └── chat_main.py       # AI对话招聘主页面
│   └── interview_page.py      # AI面试页面
│
├── agent.py                   # 兼容旧接口（已废弃）
├── agent_service.py           # 兼容旧接口（已废弃）
├── gsh.py                     # 工具脚本
├── import_jd_to_mysql.py      # JD导入脚本
└── text_data.py               # 文本数据
```

## 📦 模块职责说明

### 后端模块 (backend/)

| 模块 | 职责 | 核心功能 |
|------|------|----------|
| `config.py` | 统一配置管理 | 数据库连接、路径配置、API配置、邮箱配置 |
| `utils.py` | 工具函数 | 文本提取、文件读写、文本摘要 |
| `database.py` | 数据库操作 | MySQL连接、CRUD操作 |
| `ai_scorer.py` | AI评分 | LLM调用、简历评分、智能问答 |
| `resume_parser.py` | 简历解析 | 文件解析、信息提取 |
| `email_service.py` | 邮件服务 | 发送邮件、面试邀请 |
| `excel_service.py` | Excel操作 | 数据导出、报表生成 |
| `interview_service.py` | 面试服务 | 面试链接、题目生成、评分 |
| `log_system.py` | 日志系统 | 操作日志、对话日志 |

### 前端页面 (pages/)

| 页面 | 用途 |
|------|------|
| `pages/main/app.py` | 校园招聘投递入口 |
| `pages/main/chat_main.py` | AI对话招聘主界面 |
| `pages/interview_page.py` | AI面试页面 |

## 🔄 迁移说明

### 已废弃文件

- `agent.py` - 保留用于兼容旧代码，新代码应直接从 `backend/` 导入
- `agent_service.py` - 保留用于兼容旧代码，新代码应直接从 `backend/` 导入

### 新代码导入方式

```python
# 从 backend 模块导入
from backend.config import UPLOAD_FOLDER
from backend.database import query_jobs_from_db
from backend.ai_scorer import handle_score
```

## 🚀 启动方式

### 主应用（对话招聘）
```bash
streamlit run pages/main/chat_main.py
```

### 校园招聘页面
```bash
streamlit run pages/main/app.py
```

### 面试页面（通过邮件链接访问）
```bash
streamlit run pages/interview_page.py?token=xxx
```

## 📋 依赖安装

```bash
pip install -r requirements.txt
```

## ⚠️ 注意事项

1. 确保已配置 MySQL 数据库连接信息（在 `backend/config.py` 中）
2. 确保已配置阿里云百炼 API 密钥（在 `backend/config.py` 中）
3. 确保已配置邮件发送账号（在 `backend/config.py` 中）
