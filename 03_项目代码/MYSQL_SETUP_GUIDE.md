# 🗄️ MySQL数据库配置说明

## 📋 配置步骤

### 1. 检查MySQL是否安装

```bash
# Linux/macOS
mysql --version

# Windows
mysql.exe --version
```

### 2. 启动MySQL服务

```bash
# Linux
sudo systemctl start mysql
# 或
sudo service mysql start

# macOS
mysql.server start

# Windows
net start mysql
```

### 3. 创建数据库和用户

```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'recruitment_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON recruitment.* TO 'recruitment_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

### 4. 配置.env文件

编辑 `/workspace/04_数据文件/.env` 文件：

```env
# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=recruitment
MYSQL_CHARSET=utf8mb4
```

### 5. 修改配置文件

编辑 `/workspace/03_项目代码/config.py` 文件：

```python
# 将 USE_SQLITE 改为 False
USE_SQLITE = False
```

### 6. 初始化数据库表

运行以下命令初始化数据库表：

```bash
cd /workspace/03_项目代码
python -c "from database import init_tables; init_tables()"
```

### 7. 导入岗位数据

```bash
cd /workspace/03_项目代码
python import_jobs.py
```

---

## 📊 数据库表结构

### 表1: job_positions（岗位信息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| job_name | VARCHAR(200) | 岗位名称，唯一 |
| jd_content | TEXT | 岗位JD内容 |
| scoring_criteria | TEXT | 评分标准 |
| education | VARCHAR(100) | 学历要求 |
| city | VARCHAR(100) | 工作城市 |
| is_intern | TINYINT | 是否实习岗 |
| hiring_count | INT | 招聘人数 |
| is_open | TINYINT | 是否开放 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 表2: resume_record（简历投递记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| deliver_time | DATETIME | 投递时间 |
| name | VARCHAR(100) | 姓名 |
| gender | VARCHAR(20) | 性别 |
| age | VARCHAR(20) | 年龄 |
| education | VARCHAR(100) | 学历 |
| major | VARCHAR(200) | 专业 |
| city | VARCHAR(100) | 所在城市 |
| target_city | VARCHAR(200) | 意向城市 |
| job | VARCHAR(200) | 应聘岗位 |
| score | INT | 初筛得分 |
| email | VARCHAR(200) | 邮箱 |
| mail_status | VARCHAR(50) | 邮件状态 |
| result | VARCHAR(50) | 初筛结果 |
| interview_token | VARCHAR(200) | 面试Token |
| interview_link | VARCHAR(500) | 面试链接 |
| interview_status | VARCHAR(50) | 面试状态 |
| created_at | TIMESTAMP | 创建时间 |

### 表3: interview_record（AI面试记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| token | VARCHAR(200) | 面试Token，唯一 |
| email | VARCHAR(200) | 面试者邮箱 |
| candidate_name | VARCHAR(100) | 面试者姓名 |
| resume_name | VARCHAR(200) | 简历文件名 |
| job_name | VARCHAR(200) | 应聘岗位 |
| resume_id | INT | 关联简历ID |
| status | VARCHAR(50) | 面试状态 |
| questions_basic | TEXT | 基础知识题目(JSON) |
| questions_project | TEXT | 项目经历题目(JSON) |
| questions_intern | TEXT | 实习经历题目(JSON) |
| questions_practice | TEXT | 技能实战题目(JSON) |
| questions_advanced | TEXT | 技能进阶题目(JSON) |
| answers | TEXT | 所有回答(JSON) |
| final_score | DECIMAL(5,2) | 最终得分 |
| scoring_details | TEXT | 评分详情(JSON) |
| result | VARCHAR(50) | 面试结果 |
| interview_duration | INT | 面试用时(秒) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| expired_at | DATETIME | 链接过期时间 |

---

## 🔧 常见问题

### Q1: MySQL连接失败？

**A:** 检查以下内容：
1. MySQL服务是否启动
2. 主机地址是否正确（localhost或IP地址）
3. 端口是否正确（默认3306）
4. 用户名和密码是否正确
5. 数据库是否存在

### Q2: 权限不足？

**A:** 确保用户有足够的权限：
```sql
GRANT ALL PRIVILEGES ON recruitment.* TO 'username'@'host';
FLUSH PRIVILEGES;
```

### Q3: 字符集问题？

**A:** 确保数据库和表的字符集都是utf8mb4：
```sql
CREATE DATABASE recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Q4: 如何备份数据库？

**A:** 使用mysqldump：
```bash
mysqldump -u root -p recruitment > backup.sql
```

### Q5: 如何恢复数据库？

**A:** 使用mysql命令：
```bash
mysql -u root -p recruitment < backup.sql
```

---

## 🔄 切换回SQLite

如需切换回SQLite数据库：

1. 修改 `config.py`：
```python
USE_SQLITE = True
```

2. SQLite无需额外配置，自动创建数据库文件

---

## 📞 技术支持

如有问题，请检查：
1. MySQL错误日志
2. Python连接错误信息
3. 配置文件是否正确

---

**文档版本**：v1.0
**最后更新**：2026-05-23
