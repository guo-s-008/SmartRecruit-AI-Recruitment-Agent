import pandas as pd
import random
from datetime import datetime

# ==================== 配置 ====================
OUTPUT_PATH = r"F:\ai智能招聘系统_参赛项目\04_数据文件\text_data.xlsx"
# 岗位池
JOBS = [
    "AI大数据工程师",
    "AI算法工程师",
    "AI应用开发工程师",
    "大数据开发工程师",
    "大数据运维开发工程师",
    "数据分析师",
    "数据科学家",
    "推荐算法工程师"
]
# 城市池
CITIES = ["厦门", "长沙", "杭州", "深圳", "成都", "广州", "南京", "武汉"]
# 学历池
EDUCATIONS = ["本科", "硕士", "博士", "大专"]
# 姓名池
SURNAMES = ["陈", "李", "王", "张", "刘", "周", "赵", "黄", "林", "吴",
            "郑", "何", "罗", "杨", "孙", "胡", "朱", "高", "郭", "马", "李", "曹", "卢"]
GIVEN_NAMES_MALE = ["宇恒", "恒锐", "思雨", "浩然", "子轩", "鹏飞", "志远", "逸凡", "博文", "俊杰",
                    "昊天", "烨磊", "伟宸", "晟睿", "文博", "天佑", "文昊", "修洁", "黎昕", "远航", "吉斌", "善长"]
GIVEN_NAMES_FEMALE = ["雨涵", "梓萱", "思琪", "语嫣", "晓婷", "雪怡", "诗涵", "梦瑶", "欣怡", "静怡",
                      "婉仪", "若曦", "紫萱", "曼琳", "雅静", "悦然", "清扬", "知画", "嫣然", "碧落", "莲"]
# 日期：改为4天
DATES = ["2026-05-01", "2026-05-02", "2026-05-03",
         "2026-05-04", "2026-05-05", "2026-05-06", "2026-05-07", "2026-05-08"]
# 每天数据量：80~150 随机
MIN_ROWS = 80
MAX_ROWS = 200


# ==================== 生成函数 ====================
def random_name():
    surname = random.choice(SURNAMES)
    if random.random() < 0.6:  # 60% 男性
        given = random.choice(GIVEN_NAMES_MALE)
        gender = "男"
    else:
        given = random.choice(GIVEN_NAMES_FEMALE)
        gender = "女"
    return f"{surname}{given}", gender


def random_age(education):
    if education == "大专":
        return random.randint(20, 23)
    elif education == "本科":
        return random.randint(21, 25)
    elif education == "硕士":
        return random.randint(24, 28)
    else:
        return random.randint(29, 35)


def generate_row(row_id, date_str):
    name, gender = random_name()
    education = random.choice(EDUCATIONS)
    age = random_age(education)
    job = random.choice(JOBS)
    city = random.choice(CITIES)
    target_city = random.choice(CITIES)
    resume_score = random.randint(55, 98)

    # 初筛规则
    if resume_score >= 85:
        passed_screening = "是"
    elif resume_score < 70:
        passed_screening = "否"
    else:
        passed_screening = random.choice(["是", "否"])

    # AI面试规则
    if passed_screening == "是" and random.random() < 0.8:
        interview_done = "是"
        basic = round(random.uniform(3, 9), 1)
        project = round(random.uniform(3, 9), 1)
        intern = round(random.uniform(3, 9), 1)
        practice = round(random.uniform(3, 9), 1)
        advanced = round(random.uniform(3, 9), 1)
        total = round(basic * 0.1 + project * 0.3 + intern * 0.3 + practice * 0.2 + advanced * 0.1, 2)
        hired = "录用" if total >= 7 else "不合适"
    else:
        interview_done = "否"
        basic = None
        project = None
        intern = None
        practice = None
        advanced = None
        total = None
        hired = None

    return {
        "ID": row_id,
        "投递时间": date_str,
        "姓名": name,
        "性别": gender,
        "年龄": age,
        "学历": education,
        "投递岗位": job,
        "所在城市": city,
        "意向城市": target_city,
        "简历得分": resume_score,
        "是否通过初筛": passed_screening,
        "是否进行AI面试": interview_done,
        "基础知识得分": basic,
        "项目经历得分": project,
        "实习经历得分": intern,
        "技能实战得分": practice,
        "进阶实战得分": advanced,
        "总分": total,
        "是否录用": hired
    }


# ==================== 生成数据 ====================
global_id = 1
with pd.ExcelWriter(OUTPUT_PATH, engine='openpyxl') as writer:
    for date_str in DATES:
        # 每天随机生成 80~150 条
        daily_count = random.randint(MIN_ROWS, MAX_ROWS)
        rows = []
        for _ in range(daily_count):
            row = generate_row(global_id, date_str)
            rows.append(row)
            global_id += 1
        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name=date_str, index=False)
        print(f"✅ {date_str}：生成 {daily_count} 条数据")

print(f"\n🎉 模拟数据 Excel 已生成：{OUTPUT_PATH}")
print("可直接用于 FineBI 双数据集分析")