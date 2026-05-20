
# 智聘未来 AI 招聘系统 - 快速设置指南

## 🎉 项目状态
✅ **应用已成功启动并运行！**  
📱 访问地址: http://localhost:8501

## 📋 完成的工作

### 1. 项目重构
- ✅ 将庞大的代码拆分为单一职责的模块
- ✅ 实现了清晰的模块划分
- ✅ 保留了原有接口，确保兼容性

### 2. 数据库解决方案
由于MySQL配置复杂，我们实现了双数据库支持：

#### 📦 SQLite（当前使用 - 推荐开发环境）
- ✅ 开箱即用，无需配置服务器
- ✅ 自动初始化表结构
- ✅ 已预置3个示例岗位数据

#### 🗄️ MySQL（可选 - 生产环境）
- ✅ 保留完整的MySQL支持
- ✅ 只需在`config.py`中设置`USE_SQLITE = False`即可切换

### 3. 初始化数据
已在SQLite数据库中预置以下岗位：
- AI大数据工程师 (北京/杭州)
- 大数据开发工程师 (深圳)
- 数据分析师 (广州, 含实习岗)

## 🚀 快速开始

### 查看应用
应用已在运行中，直接访问: http://localhost:8501

### 如果需要重启应用
```bash
cd /workspace/03_项目代码
streamlit run pages/main/chat_main.py
```

### 初始化数据（如需要）
```bash
python3 init_db_data.py
```

## 📁 项目结构

```
03_项目代码/
├── config.py                 # 统一配置管理
├── utils.py                  # 通用工具函数
├── database.py               # 数据库操作（自动切换）
├── database_sqlite.py        # SQLite数据库实现
├── ai_scorer.py              # AI评分模块
├── resume_parser.py          # 简历解析
├── email_service.py          # 邮件服务
├── excel_service.py          # Excel操作
├── interview_service.py      # 面试服务（自动切换）
├── interview_service_sqlite.py # SQLite面试服务实现
├── log_system.py             # 日志系统
│
├── pages/                    # 前端页面
│   ├── main/
│   │   ├── chat_main.py      # 主应用 - AI对话招聘
│   │   └── app.py            # 校园招聘页面
│   └── interview_page.py     # AI面试页面
│
├── init_db_data.py           # 数据库初始化脚本
├── agent.py                  # 兼容性文件（已废弃）
├── agent_service.py          # 兼容性文件（已废弃）
└── MODULES_README.md         # 模块详细说明
```

## 🔧 配置说明

### 切换数据库
编辑 `config.py`:
```python
# 使用SQLite（默认）
USE_SQLITE = True

# 或使用MySQL
USE_SQLITE = False
```

### 环境变量
创建 `/workspace/04_数据文件/.env` 文件配置：
```env
# API配置
API_KEY=your_api_key
API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_MODEL=qwen-turbo

# MySQL配置（如使用MySQL）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=recruitment
MYSQL_CHARSET=utf8mb4

# 邮件配置
MAIL_SENDER=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_SERVER=smtp.example.com
MAIL_PORT=465
HR_EMAIL=hr@company.com
```

## 💡 主要功能

1. **AI 对话招聘** - 智能对话，岗位推荐，简历解析
2. **简历评分** - AI自动评分，匹配度分析
3. **邮件通知** - 自动发送录用/拒信
4. **AI 面试** - 个性化面试题目，自动评分
5. **数据记录** - 记录所有招聘流程数据

## 📞 下一步

- [ ] 上传真实的 JD 数据
- [ ] 配置 API Key
- [ ] 配置邮件服务
- [ ] 测试完整招聘流程

## 🔍 常见问题

### 如何添加新岗位？
1. 可以修改 `init_db_data.py` 重新运行
2. 或者直接在数据库中插入数据

### 如何查看数据库内容？
SQLite数据库文件位置: `/workspace/04_数据文件/recruitment.db`

### 应用无法启动？
检查端口8501是否被占用，或修改启动命令使用其他端口

---

✅ **项目已准备就绪，祝您使用愉快！**
