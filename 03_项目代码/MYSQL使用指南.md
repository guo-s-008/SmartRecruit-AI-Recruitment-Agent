
# MySQL数据库集成使用指南

## 📋 概述

本项目已完整集成MySQL数据库，支持从SQLite无缝切换到MySQL。所有功能（岗位管理、人才库、简历记录、面试记录等）都已适配MySQL。

---

## 🔧 配置步骤

### 1. 安装依赖

确保已安装pymysql：

```bash
pip install pymysql
```

### 2. 配置环境变量

在 `04_数据文件/.env` 文件中配置MySQL连接信息：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=recruitment
MYSQL_CHARSET=utf8mb4

# 其他配置保持不变...
```

### 3. 切换到MySQL

在 `03_项目代码/config.py` 中修改：

```python
USE_SQLITE = False  # 改为False使用MySQL
```

---

## 🚀 快速开始

### 1. 测试连接

运行集成测试脚本：

```bash
cd 03_项目代码
python test_mysql_integration.py
```

这个脚本会：
- 检查配置
- 测试MySQL连接
- 初始化数据库表
- 测试增删改查功能

### 2. 初始化测试数据

运行测试数据初始化脚本：

```bash
python init_mysql_test_data.py
```

这个脚本会：
- 创建所有必需的表
- 从 `04_数据文件/job_jd` 目录加载岗位
- 添加8个测试人才到人才库

---

## 📊 数据库表结构

### 1. job_positions - 岗位表
存储所有招聘岗位信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| job_name | VARCHAR(200) | 岗位名称，唯一 |
| jd_content | TEXT | 岗位描述 |
| scoring_criteria | TEXT | 评分标准 |
| education | VARCHAR(100) | 学历要求 |
| city | VARCHAR(100) | 工作城市 |
| is_intern | TINYINT | 是否实习岗 |
| hiring_count | INT | 招聘人数 |
| is_open | TINYINT | 是否开放 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2. resume_record - 简历记录表
存储所有投递的简历信息

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
| interview_token | VARCHAR(200) | 面试token |
| interview_link | VARCHAR(500) | 面试链接 |
| interview_status | VARCHAR(50) | 面试状态 |
| created_at | TIMESTAMP | 创建时间 |

### 3. interview_record - 面试记录表
存储AI面试的详细记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| token | VARCHAR(200) | 面试token，唯一 |
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

### 4. interview_url - 面试URL表
管理面试链接的访问控制

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| resume_id | INT | 关联简历ID，外键 |
| url | VARCHAR(500) | 面试URL |
| token | VARCHAR(200) | 面试token |
| generated_at | TIMESTAMP | URL生成时间 |
| used_at | TIMESTAMP | 使用时间 |
| destroyed_at | TIMESTAMP | 销毁时间 |
| request_count | INT | 请求次数 |
| interrupted | INT | 是否中断 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 5. talent_pool - 人才库表
存储所有人才信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| name | VARCHAR(100) | 姓名 |
| gender | VARCHAR(20) | 性别 |
| age | VARCHAR(20) | 年龄 |
| education | VARCHAR(100) | 学历 |
| major | VARCHAR(200) | 专业 |
| city | VARCHAR(100) | 所在城市 |
| email | VARCHAR(200) | 邮箱，唯一 |
| phone | VARCHAR(20) | 电话 |
| skills | TEXT | 技能 |
| experience | TEXT | 经验 |
| resume_text | TEXT | 简历内容 |
| tags | TEXT | 标签 |
| last_updated | TIMESTAMP | 最后更新时间 |
| status | VARCHAR(50) | 状态 |
| source | VARCHAR(100) | 来源 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 🛠️ API函数说明

### 岗位管理
- `add_job_to_db(job_data)` - 添加/更新岗位
- `get_all_jobs()` - 获取所有岗位
- `query_jobs_from_db(keyword)` - 查询岗位（支持关键词搜索）
- `get_jd_from_db(job_name)` - 获取岗位描述
- `update_job_status(job_id, is_open)` - 更新岗位状态
- `delete_job(job_id)` - 删除岗位

### 人才库管理
- `add_talent_to_pool(talent_data)` - 添加/更新人才
- `get_all_talents(status)` - 获取所有人才（可按状态筛选）
- `search_talents(keyword, education, city, skills)` - 搜索人才
- `recommend_talents_for_job(job_name, limit)` - 为岗位推荐人才
- `update_talent_status(talent_id, status)` - 更新人才状态

### 简历和面试
- `save_to_mysql(data)` - 保存简历记录
- `handle_save_to_db(detail_data)` - 保存简历记录（封装接口）
- `save_interview_url(resume_id, url, token)` - 保存面试URL
- `update_interview_url_request(token)` - 更新URL访问次数
- `get_interview_url_by_token(token)` - 通过token获取URL
- `mark_interview_url_destroyed(token)` - 标记URL为销毁
- `get_all_resumes()` - 获取所有简历
- `get_all_interviews()` - 获取所有面试记录

---

## 📝 使用示例

### 1. 添加岗位

```python
from database import add_job_to_db

job_data = {
    "job_name": "Python开发工程师",
    "jd_content": "负责后端开发工作...",
    "scoring_criteria": "技术能力40%，项目经验30%...",
    "education": "本科",
    "city": "北京",
    "is_intern": 0,
    "hiring_count": 2,
    "is_open": 1
}

job_id = add_job_to_db(job_data)
print(f"岗位添加成功，ID: {job_id}")
```

### 2. 添加人才

```python
from database import add_talent_to_pool

talent_data = {
    "name": "张三",
    "gender": "男",
    "age": "26",
    "education": "硕士",
    "major": "计算机科学",
    "city": "北京",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "skills": "Python, Java, SQL",
    "experience": "3年开发经验",
    "resume_text": "简历内容...",
    "tags": "后端, 全栈",
    "source": "简历投递"
}

talent_id = add_talent_to_pool(talent_data)
print(f"人才添加成功，ID: {talent_id}")
```

### 3. 查询和搜索

```python
from database import get_all_jobs, get_all_talents, search_talents

# 获取所有岗位
jobs = get_all_jobs()
for job in jobs:
    print(f"岗位: {job['job_name']}, 城市: {job['city']}")

# 获取所有人才
talents = get_all_talents()
for talent in talents:
    print(f"人才: {talent['name']}, 邮箱: {talent['email']}")

# 搜索人才
results = search_talents(
    keyword="Python",
    education="本科",
    city="北京"
)
print(f"找到 {len(results)} 个匹配人才")
```

---

## 🎯 HR后台管理

项目包含完整的HR后台管理系统，支持：

1. **仪表盘** - 查看统计数据、快速操作、岗位推荐
2. **岗位管理** - 查看、添加、编辑、删除岗位
3. **人才库** - 查看、搜索、筛选、邀请面试
4. **简历管理** - 查看所有投递记录
5. **面试管理** - 查看面试进度和结果

访问HR后台：
- 启动Streamlit应用后访问 `pages/hr/hr_dashboard.py`
- 或通过主页面的导航进入

---

## 🔄 切换回SQLite

如果需要切换回SQLite，只需：

1. 修改 `config.py`：
   ```python
   USE_SQLITE = True
   ```

2. 原SQLite数据库文件位于 `04_数据文件/recruitment.db`

---

## ⚠️ 注意事项

1. **字符编码**：确保MySQL数据库使用 `utf8mb4` 字符集，支持emoji和特殊字符
2. **外键约束**：删除岗位时需要先处理关联的简历记录
3. **备份**：定期备份MySQL数据库
4. **权限**：确保MySQL用户有足够的权限（CREATE, INSERT, UPDATE, DELETE, SELECT）

---

## 🐛 常见问题

### Q: 连接MySQL失败怎么办？
A: 检查以下几点：
1. MySQL服务是否启动
2. 用户名密码是否正确
3. 端口是否正确（默认3306）
4. 防火墙是否阻止连接
5. 用户是否有远程访问权限

### Q: 如何创建数据库？
A: `init_tables()` 函数会自动创建数据库（如果不存在），也可以手动创建：
```sql
CREATE DATABASE recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Q: 数据会丢失吗？
A: 从SQLite切换到MySQL不会自动迁移数据，需要手动导出导入。建议先备份SQLite数据。

---

## 📚 相关文件

- `config.py` - 配置文件
- `database.py` - MySQL数据库操作
- `database_sqlite.py` - SQLite数据库操作
- `test_mysql_integration.py` - MySQL集成测试
- `init_mysql_test_data.py` - 测试数据初始化
- `pages/hr/hr_dashboard.py` - HR后台管理
