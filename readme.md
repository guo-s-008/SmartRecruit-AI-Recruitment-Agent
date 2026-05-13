# 🤖 智聘未来 · AI 全流程智能招聘系统


## ✨ 核心功能

- **AI 对话投递**：自然语言交互，告别死板表单
- **AI 简历评分**：四维度结构化打分 + 改进建议 + 邮件回执
- **限时 AI 面试**：48h有效链接，基于简历实时生成面试题
- **HR 管理后台**：投递查看、面试复核、人工二次评分
- **数据驾驶舱**：FineBI 报表，招聘漏斗、AI信度验证、能力雷达图

## 🛠️ 技术栈

| 模块 | 技术选型 |
|------|---------|
| 前端 | Streamlit |
| 大模型 | 阿里云百炼 API (Qwen-Turbo) |
| 数据库 | MySQL |
| 报表 | FineBI |
| 邮件 | SMTP |

## 🚀 快速启动

1. **克隆仓库**

  git clone https://github.com/你的用户名/仓库名.git

2. **安装依赖**

  pip install -r requirements.txt

3. **配置环境变量**（`04_数据文件/.env`）

  API_KEY=你的阿里云API Key
  MYSQL_HOST=localhost
  MAIL_SENDER=你的邮箱

4. **启动**

  streamlit run chat_main.py

5. 可选内容
  python text_data.py   bi表测试数据生成
  python gsh.py         将txt类型的jd标准化
  python import_jd_to_mysql.py 将jd写入mysql（txt）
  python app.py 第一版的交互页面streamlit

## 📊 FineBI 报表

配套《FineBI报表实施文档》，详见 `docs/` 目录。

## 📄 License

MIT License