
# 🚀 本地部署指南

## ✅ 部署已完成！

您的 **智聘未来 · AI 全流程智能招聘系统** 已经成功部署到本地！

---

## 🌐 访问地址

应用已启动，您可以通过以下地址访问：

| 应用 | 访问地址 |
|------|---------|
| 主应用（求职者入口） | http://localhost:8501 |
| HR后台管理 | http://localhost:8501/pages/hr/hr_dashboard.py |

---

## 📦 已完成的部署步骤

✅ 1. **依赖安装** - 所有Python依赖包已安装
✅ 2. **环境配置** - API Key、邮箱等配置已完成
✅ 3. **数据库初始化** - 使用SQLite（无需服务器）
✅ 4. **测试数据** - 8个测试人才、9个测试岗位已添加
✅ 5. **应用启动** - Streamlit应用已在8501端口运行

---

## 🎯 功能模块

### 主应用（求职者入口）
- 🤖 AI对话投递 - 自然语言交互
- 📊 AI简历评分 - 四维度结构化打分
- 💌 邮件回执 - 自动发送面试通知
- 🎤 限时AI面试 - 48小时有效链接

### HR后台管理
- 📋 人才库管理 - 查看、筛选、编辑
- 🏢 岗位管理 - 发布、编辑、删除
- ⚖️ 候选人对比 - 多候选人AI智能分析
- 🔍 自动化筛选 - 多维度筛选 + 智能推荐
- 📊 数据统计 - 招聘进度查看

---

## 🔧 修改代码

**是的！您完全可以对本地代码进行修改！**

### 项目结构
```
/workspace/
├── 03_项目代码/
│   ├── pages/
│   │   ├── main/              # 主应用页面
│   │   │   ├── chat_main.py   # 主聊天页面
│   │   │   └── app.py         # 旧版应用
│   │   ├── hr/                # HR后台页面
│   │   │   ├── hr_dashboard.py
│   │   │   ├── candidate_comparison.py
│   │   │   └── auto_filter.py
│   │   └── interview_page.py  # 面试页面
│   ├── ai_scorer.py           # AI评分模块
│   ├── config.py              # 配置文件
│   ├── database.py            # MySQL数据库操作
│   ├── database_sqlite.py     # SQLite数据库操作
│   ├── email_service.py       # 邮件服务
│   ├── log_system.py          # 日志系统
│   └── resume_parser.py       # 简历解析
├── 04_数据文件/
│   ├── job_jd/                # 岗位JD文件
│   ├── recruitment.db         # SQLite数据库
│   └── .env                   # 环境变量
└── requirements.txt           # 依赖列表
```

### 常见修改点

#### 1. 修改配置
编辑 `/workspace/03_项目代码/config.py`
- `USE_SQLITE` - 切换SQLite/MySQL
- API配置、数据库配置等

#### 2. 修改AI提示词
编辑 `/workspace/03_项目代码/ai_scorer.py`
- `analyze_candidates_comparison()` - 候选人对比分析
- `ai_score_resume_with_jd()` - 简历评分
- 其他AI相关函数

#### 3. 修改页面样式和功能
编辑 `/workspace/03_项目代码/pages/` 目录下的文件
- Streamlit页面可以直接修改
- 修改后刷新浏览器即可看到效果

#### 4. 添加新功能
- 在 `03_项目代码/` 目录下创建新模块
- 在 `pages/` 目录下创建新页面（Streamlit会自动识别）

#### 5. 数据库操作
- `database.py` - MySQL操作
- `database_sqlite.py` - SQLite操作
- 添加新的表或函数

---

## 🔄 重启应用

如果修改了代码，需要重启应用：

```bash
# 1. 停止当前运行的应用（Ctrl+C）
# 2. 重新启动
cd /workspace
streamlit run 03_项目代码/pages/main/chat_main.py
```

---

## 💾 数据管理

### SQLite数据库
- 位置：`/workspace/04_数据文件/recruitment.db`
- 可以用DB Browser for SQLite等工具查看
- 适合开发和测试

### 切换到MySQL
如果需要使用MySQL：

1. 确保本地MySQL已安装并运行
2. 编辑 `04_数据文件/.env`，设置正确的MySQL密码
3. 编辑 `03_项目代码/config.py`，设置 `USE_SQLITE = False`
4. 重启应用

---

## 📖 快速参考

### 常用命令
```bash
# 安装依赖
pip install -r requirements.txt

# 启动主应用
cd /workspace
streamlit run 03_项目代码/pages/main/chat_main.py

# 启动HR后台
cd /workspace
streamlit run 03_项目代码/pages/hr/hr_dashboard.py

# 初始化测试数据
cd /workspace/03_项目代码
python add_test_data.py
```

### 文件说明
| 文件 | 说明 |
|------|------|
| `config.py` | 全局配置 |
| `database.py` | MySQL数据库操作 |
| `database_sqlite.py` | SQLite数据库操作 |
| `ai_scorer.py` | AI分析和评分 |
| `email_service.py` | 邮件发送 |
| `log_system.py` | 日志记录 |

---

## 🛟 常见问题

**Q: 修改代码后看不到效果？**
A: Streamlit会自动检测文件变化并重新加载，或者手动刷新浏览器。

**Q: 如何添加新的岗位？**
A: 有两种方式：
   1. 在HR后台页面手动添加
   2. 在 `04_数据文件/job_jd/` 目录下添加JD文件，然后运行导入脚本

**Q: 数据会丢失吗？**
A: 不会。数据保存在SQLite数据库文件中，只要不删除文件，数据就会保留。

**Q: 可以在手机上访问吗？**
A: 可以！确保电脑和手机在同一网络，使用显示的Network URL访问。

---

## 🎉 开始使用

现在您可以：
1. 在浏览器中访问 http://localhost:8501 体验主应用
2. 访问 http://localhost:8501/pages/hr/hr_dashboard.py 查看HR后台
3. 修改任何代码文件，然后刷新浏览器查看效果

**祝您使用愉快！如有任何问题，随时可以询问！**

