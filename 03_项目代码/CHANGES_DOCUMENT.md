# 📝 系统改动文档

## 📅 日期：2026-05-23

---

## 🎯 本次改动概述

本次改动主要实现以下功能：

1. **重构日志系统** - 实现4类日志分类管理
2. **完善MySQL数据库支持** - 优化数据库表结构和功能
3. **改进邮件日志记录** - 按初筛结果自动分类
4. **添加AI面试日志** - 完整记录面试过程
5. **新增HR操作日志** - 记录HR对岗位的管理操作

---

## 📂 文件改动清单

### 1. **log_system.py** - 日志系统重构

#### 改动内容：
- ✅ 重构为4类日志系统
- ✅ 新增会话日志功能（按会话ID记录）
- ✅ 新增邮件日志功能（按初筛结果分类）
- ✅ 新增AI面试日志功能（按面试者姓名记录）
- ✅ 新增HR操作日志功能（记录增删改查）
- ✅ 保留原有函数（兼容性）

#### 新增函数：
```python
# 会话日志
def create_session_log(session_id)  # 创建会话日志文件夹
def write_session_log(session_id, role, content)  # 写入会话日志

# 邮件日志
def write_email_log(candidate_name, email, job_name, score, result, 
                    applicant_email_content, hr_email_content)  
# 按初筛结果（初筛通过/初筛未通过）分类记录邮件

# AI面试日志
def write_interview_log(candidate_name, interview_data)  
# 记录完整面试信息（JSON格式）
def write_interview_detail_log(candidate_name, module, question, answer, 
                                score, scoring_reason)  
# 记录每道题的详细评分

# HR操作日志
def write_hr_log(operation_type, operator, target, before_data, 
                  after_data, remark)  
# 记录HR的增删改查操作
```

#### 日志目录结构：
```
/workspace/07_系统日志/
├── log_dialog/              # 会话日志
│   └── 2026-05-23/
│       └── session_xxx/     # 按会话ID
│           └── conversation.log
├── log_email/               # 邮件日志
│   ├── 初筛通过/            # 初筛通过
│   │   └── 张三_20260523_153045.txt
│   └── 初筛未通过/          # 初筛未通过
│       └── 李四_20260523_153046.txt
├── log_interview/           # AI面试日志
│   └── 张三/                # 按面试者姓名
│       ├── interview_20260523_153047.json
│       └── interview_detail.log
└── log_hr/                  # HR操作日志
    └── hr_2026-05-23.log
```

---

### 2. **config.py** - 数据库配置修改

#### 改动内容：
- ✅ 将 `USE_SQLITE` 从 `True` 改为 `False`
- ✅ 启用MySQL数据库支持
- ✅ 完善MySQL配置项

#### 修改配置：
```python
# 数据库配置
USE_SQLITE = False  # 改用MySQL数据库

# MySQL 数据库配置（生产环境使用）
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "recruitment",
    "charset": "utf8mb4"
}
```

---

### 3. **database.py** - MySQL数据库支持

#### 改动内容：
- ✅ 新增MySQL数据库初始化函数
- ✅ 完善3个核心表结构
- ✅ 新增面试记录保存函数
- ✅ 新增面试结果更新函数
- ✅ 新增查询函数（简历、面试）

#### 数据库表结构：

##### 表1: job_positions（岗位信息表）
```sql
CREATE TABLE job_positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(200) UNIQUE NOT NULL COMMENT '岗位名称',
    jd_content TEXT COMMENT '岗位JD内容',
    scoring_criteria TEXT COMMENT '评分标准',
    education VARCHAR(100) COMMENT '学历要求',
    city VARCHAR(100) COMMENT '工作城市',
    is_intern TINYINT DEFAULT 0 COMMENT '是否实习岗',
    hiring_count INT DEFAULT 1 COMMENT '招聘人数',
    is_open TINYINT DEFAULT 1 COMMENT '是否开放',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

##### 表2: resume_record（简历投递记录表）
```sql
CREATE TABLE resume_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deliver_time DATETIME COMMENT '投递时间',
    name VARCHAR(100) COMMENT '姓名',
    gender VARCHAR(20) COMMENT '性别',
    age VARCHAR(20) COMMENT '年龄',
    education VARCHAR(100) COMMENT '学历',
    major VARCHAR(200) COMMENT '专业',
    city VARCHAR(100) COMMENT '所在城市',
    target_city VARCHAR(200) COMMENT '意向城市',
    job VARCHAR(200) COMMENT '应聘岗位',
    score INT COMMENT '初筛得分',
    email VARCHAR(200) COMMENT '邮箱',
    mail_status VARCHAR(50) COMMENT '邮件状态',
    result VARCHAR(50) COMMENT '初筛结果',
    interview_token VARCHAR(200) COMMENT '面试Token',
    interview_link VARCHAR(500) COMMENT '面试链接',
    interview_status VARCHAR(50) DEFAULT 'pending' COMMENT '面试状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

##### 表3: interview_record（AI面试记录表）
```sql
CREATE TABLE interview_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(200) UNIQUE NOT NULL COMMENT '面试Token',
    email VARCHAR(200) COMMENT '面试者邮箱',
    candidate_name VARCHAR(100) COMMENT '面试者姓名',
    resume_name VARCHAR(200) COMMENT '简历文件名',
    job_name VARCHAR(200) COMMENT '应聘岗位',
    resume_id INT COMMENT '关联简历ID',
    status VARCHAR(50) DEFAULT 'pending' COMMENT '面试状态',
    questions_basic TEXT COMMENT '基础知识题目(JSON)',
    questions_project TEXT COMMENT '项目经历题目(JSON)',
    questions_intern TEXT COMMENT '实习经历题目(JSON)',
    questions_practice TEXT COMMENT '技能实战题目(JSON)',
    questions_advanced TEXT COMMENT '技能进阶题目(JSON)',
    answers TEXT COMMENT '所有回答(JSON)',
    final_score DECIMAL(5,2) COMMENT '最终得分',
    scoring_details TEXT COMMENT '评分详情(JSON)',
    result VARCHAR(50) COMMENT '面试结果',
    interview_duration INT COMMENT '面试用时(秒)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expired_at DATETIME COMMENT '链接过期时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 新增函数：
```python
def init_tables()  # 初始化数据库表
def save_interview_to_db(interview_data)  # 保存面试记录
def update_interview_result(token, final_score, result, scoring_details)  # 更新面试结果
def get_all_resumes()  # 获取所有简历记录
def get_all_interviews()  # 获取所有面试记录
```

---

### 4. **email_service.py** - 邮件服务优化

#### 改动内容：
- ✅ 集成新的邮件日志功能
- ✅ 所有邮件自动记录到日志系统
- ✅ 面试邀请邮件也记录到日志
- ✅ 新增候选人姓名参数

#### 修改函数：
```python
def send_email(receive_email, score, job_title, apply_result, 
               report="", advantage="", shortcoming="", 
               candidate_name="")  # 新增candidate_name参数

def handle_send_email(receive_email, score, job_title, apply_result, 
                     report="", advantage="", shortcoming="", 
                     candidate_name="")  # 新增candidate_name参数
```

---

### 5. **新增文件**

#### test_mysql_and_logs.py - 完整测试脚本
测试内容包括：
- ✅ MySQL数据库连接测试
- ✅ 4类日志系统测试
- ✅ 邮件发送测试
- ✅ 简历评分测试
- ✅ 日志目录结构查看

---

## 🔧 使用说明

### 1. 启动MySQL服务

确保MySQL服务已启动：
```bash
mysql.server start  # macOS
systemctl start mysql  # Linux
net start mysql  # Windows
```

### 2. 配置数据库连接

编辑 `.env` 文件：
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=recruitment
```

### 3. 运行测试

```bash
cd /workspace/03_项目代码
python test_mysql_and_logs.py
```

### 4. 查看日志

日志目录：`/workspace/07_系统日志/`

查看日志目录结构：
```bash
find /workspace/07_系统日志 -type f -name "*.log" -o -name "*.txt" -o -name "*.json"
```

---

## 📋 功能流程

### 完整招聘流程

```
1. 候选人上传简历
   ↓
2. AI初筛评分（≥70分通过）
   ↓
3. 发送初筛结果邮件
   ├→ 发送给求职者
   ├→ 发送给HR
   └→ 记录到日志（按结果分类）
   ↓
4. 初筛通过者 → 发送AI面试邀请
   ├→ 发送给求职者
   ├→ 发送给HR
   └→ 记录到日志（面试邀请）
   ↓
5. 候选人进入AI面试
   ├→ AI生成针对性问题
   ├→ 候选人回答
   ├→ AI评分
   └→ 完整记录到日志（面试详细日志）
   ↓
6. 发送面试结果邮件
   ├→ 发送给求职者
   ├→ 发送给HR
   └→ 记录到日志
   ↓
7. HR查看数据库 → 决定后续流程
   └→ HR操作记录到日志
```

---

## ⚠️ 注意事项

1. **MySQL连接问题**：如果MySQL未启动或配置错误，程序会报错
2. **切换数据库**：如需使用SQLite，将 `config.py` 中的 `USE_SQLITE` 改为 `True`
3. **日志清理**：定期清理 `/workspace/07_系统日志/` 下的日志文件
4. **权限问题**：确保运行程序的用户有权限读写日志目录

---

## 🎯 下一步开发

1. **HR后台管理系统** - 待开发
2. **面试结果数据分析** - 待开发
3. **候选人管理系统** - 待开发
4. **数据可视化** - 待开发

---

## 📞 技术支持

如有问题，请检查：
1. MySQL服务是否运行
2. .env配置文件是否正确
3. 日志目录是否有写入权限
4. API Key是否配置正确

---

**文档版本**：v1.0
**最后更新**：2026-05-23
**维护者**：智聘未来技术团队
