
import os
import shutil
import pandas as pd
import time
import re
import requests
from docx import Document
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pymysql
from pymysql import Error
from log_system import write_recruit_log

# ---------------------- 1. 加载环境配置 ----------------------
load_dotenv("../04_数据文件/.env")

# 文件夹路径
UPLOAD_FOLDER = "../01_简历投递收件箱"
PROCESSED_FOLDER = "../02_已处理简历"
# DATA_FILE = "../04_数据文件/recruitment_data.xlsx" # 旧路径，现在用 detail 文件
JD_FOLDER = "../04_数据文件/job_jd"  # 【新增】JD文件夹路径

# ---------------------- MySQL配置（从.env读取） ----------------------
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")

# 大模型API配置
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

# ===================== ✅ 邮箱配置 =====================
MAIL_SENDER = os.getenv("MAIL_SENDER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.qq.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 465))

os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 全局变量：接收前端传递的选中岗位（供app.py赋值）
SELECTED_JOB_FROM_WEB = None


# ---------------------- 2. 读取简历 ----------------------
def read_resume_text(file_path):
    text = ""
    suffix = file_path.split(".")[-1].lower()
    try:
        if suffix == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif suffix == "docx":
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif suffix == "pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return ""
    return text


# ---------------------- 3. 【核心修改】根据前端传入岗位读取对应JD，废弃自动匹配逻辑 ----------------------
def get_matched_jd_content(job_name):
    print("[DEBUG] 接收岗位名：", job_name)
    """
    根据前端app.py传入的选中岗位名称，直接读取对应岗位的JD文件
    文件命名规范：岗位名_jd.txt
    """
    if not os.path.exists(JD_FOLDER):
        print(f"⚠️ 警告：JD文件夹不存在 {JD_FOLDER}，使用默认JD。")
        return "大数据开发工程师要求：熟悉Spark、Flink、数仓建模、SQL调优"

    try:
        # 拼接对应岗位的JD文件名
        target_jd_file = f"{job_name}_jd.txt"
        target_jd_path = os.path.join(JD_FOLDER, target_jd_file)

        # 判断对应岗位JD文件是否存在
        if os.path.exists(target_jd_path):
            with open(target_jd_path, "r", encoding="utf-8") as f:
                print(f"✅ 读取前端指定岗位JD：{target_jd_file}")
                return f.read().strip()
        else:
            # 无对应岗位JD则读取默认第一个JD文件
            files = [f for f in os.listdir(JD_FOLDER) if f.endswith(".txt")]
            if not files:
                return "未找到JD文件"
            default_file = files[0]
            default_path = os.path.join(JD_FOLDER, default_file)
            with open(default_path, "r", encoding="utf-8") as f:
                print(f"⚠️ 未找到【{job_name}】对应JD，使用默认JD：{default_file}")
                return f.read().strip()

    except Exception as e:
        print(f"❌ 读取JD文件夹失败：{e}")
        return "大数据开发工程师要求：熟悉Spark、Flink、数仓建模、SQL调优"


# ---------------------- 4. 提取邮箱 ----------------------
def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    res = re.findall(pattern, text)
    return res[0] if res else None


# ---------------------- 5. AI 打分 ----------------------
# 重写 ai_score_resume 以支持传入 JD 内容
def ai_score_resume_with_jd(resume_text, jd_content, job_name="匹配到的岗位"):
    prompt = f"""
你是专业HR面试官，根据【岗位JD】对简历进行严格评分（满分100）。

【岗位名称】
{job_name}

【岗位JD要求】
{jd_content}

【简历内容】
{resume_text[:3000]}

请严格按以下格式输出：

【简历评分】
分数：xx

【分项评分标准】
1. 专业匹配度：xx分
2. 技能匹配度：xx分
3. 项目经验匹配度：xx分
4. 综合素养：xx分

【简历优势】
xxx

【简历不足与改进建议】
xxx
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=35)
        res_json = response.json()

        if "choices" in res_json:
            content = res_json["choices"][0]["message"]["content"]
        else:
            content = f"AI返回异常：{str(res_json)}"
    except Exception as e:
        content = f"AI调用失败：{str(e)}"
        score = 0
        return score, content

    score = 0
    num_list = re.findall(r"分数[:：]\s*(\d+)", content)
    if num_list:
        score = int(num_list[0])

    # 录取 / 不录取 话术
    if score >= 85:
        final_msg = f"""
——————————————
【录用结果通知】
恭喜同学，你的简历综合得分：{score}分，
你的简历符合岗位录用标准，
欢迎加入智聘未来团队，
后续将通过邮件通知面试安排，请耐心等待。
"""
    else:
        final_msg = f"""
——————————————
【录用结果通知】
很遗憾，你的简历综合得分：{score}分，
暂时与岗位要求存在差距，
建议结合改进建议优化简历，
欢迎再次投递。
"""

    return score, content + final_msg


# ---------------------- 6. 发送双向邮件（含控制台完整打印+日志保存 + 中文错误捕获 + 悲观失败机制） ----------------------
def send_email(receive_email, score, job_title, apply_result, report="", advantage="", shortcoming=""):
    HR_EMAIL = os.getenv("HR_EMAIL")
    mail_status = "失败"

    # 直接使用传入的录用结果，不再比较分数
    if apply_result == "录用":
        hr_tip = f"请您联系求职者邮箱：{receive_email}，尽快安排后续面试。"
    else:
        hr_tip = "该候选人已为您录入企业人才库，可后续持续关注。"

    advantage_text = advantage if advantage else "无明显优势信息"
    shortcoming_text = shortcoming if shortcoming else "无明显短板信息"

    # 求职者邮件使用完整的评分报告
    applicant_content = report if report else "AI评分报告生成失败"

    hr_content = f"""【简历评分】
综合得分：{score}分
录用判定：{apply_result}

【简历优势】
{advantage_text}

【简历不足与改进建议】
{shortcoming_text}

【HR处理提示】
{hr_tip}
"""

    # 打印日志（保持不变）
    print("\n" + "="*80)
    print("📄 求职者邮件全文：")
    print("="*80)
    print(applicant_content)
    print("\n" + "="*80)
    print("📄 HR邮件全文：")
    print("="*80)
    print(hr_content)
    print("="*80 + "\n")

    log_dir = "../07_系统日志/log_eminfo"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"email_{time.strftime('%Y-%m-%d')}.log")
    log_content = f"""
[时间] {time.strftime('%Y-%m-%d %H:%M:%S')}
[收件人] {receive_email}
[HR邮箱] {HR_EMAIL}
[得分] {score}
[结果] {apply_result}

------ 求职者邮件 ----
{applicant_content}

------ HR邮件 ----
{hr_content}

{'='*60}
"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content)
    print(f"📝 邮件内容已保存至日志：{log_file}")

    try:
        if not receive_email:
            print("❌ 错误：简历中未提取到邮箱，无法发送")
            return mail_status

        msg1 = MIMEMultipart()
        msg1["From"] = MAIL_SENDER
        msg1["To"] = receive_email
        msg1["Subject"] = "【智聘未来】你的简历测评结果"
        msg1.attach(MIMEText(applicant_content, "plain", "utf-8"))
        smtp = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtp.login(MAIL_SENDER, MAIL_PASSWORD)
        smtp.sendmail(MAIL_SENDER, receive_email, msg1.as_string())
        smtp.quit()
        print("✅ 求职者邮件发送成功")

        if HR_EMAIL:
            msg2 = MIMEMultipart()
            msg2["From"] = MAIL_SENDER
            msg2["To"] = HR_EMAIL
            msg2["Subject"] = f"【智聘未来】简历投递通知｜得分：{score}｜{apply_result}"
            msg2.attach(MIMEText(hr_content, "plain", "utf-8"))
            smtp2 = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
            smtp2.login(MAIL_SENDER, MAIL_PASSWORD)
            smtp2.sendmail(MAIL_SENDER, HR_EMAIL, msg2.as_string())
            smtp2.quit()
            print("✅ HR精简邮件发送成功")

        mail_status = "成功"

    except smtplib.SMTPAuthenticationError:
        print("❌ 错误：邮箱授权码/密码错误，请检查.env配置")
    except smtplib.SMTPConnectError:
        print("❌ 错误：无法连接QQ邮箱服务器，检查网络/端口")
    except smtplib.SMTPRecipientsRefused:
        print("❌ 错误：对方邮箱不存在/被拒收/黑名单")
    except smtplib.SMTPHeloError:
        print("❌ 错误：邮箱服务器验证失败")
    except TimeoutError:
        print("❌ 错误：发送超时，网络不稳定")
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")

    print(f"\n📌 最终邮件状态：{mail_status}")
    return mail_status
# ---------------------- 7.MySQL保存函数 ----------------------
def save_to_mysql(data):
    """
    data 是 dict，和 detail_data 结构一致
    返回插入后的自增 ID
    """
    conn = None
    cursor = None
    inserted_id = None
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset=MYSQL_CHARSET,
            autocommit=True
        )
        cursor = conn.cursor()

        sql = """
        INSERT INTO resume_record 
        (deliver_time, job, major, education, city, target_city, score, email, mail_status, result) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data["投递时间"],
            data["岗位"],
            data["专业"],
            data["学历"],
            data["所在城市"],
            data["意向地区"],
            data["得分"],
            data["邮箱"],
            data["邮件状态"],
            data["测评结果"]
        ))

        # 获取刚插入的 ID（兼容性更好）
        cursor.execute("SELECT LAST_INSERT_ID()")
        inserted_id = cursor.fetchone()[0]

        print("✅ 数据已存入 MySQL，ID:", inserted_id)
    except Error as e:
        print("❌ MySQL 错误：", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return inserted_id  # 返回 ID，失败时为 None
# ---------------------- 8. 处理简历 ----------------------
def process_new_files():
    global SELECTED_JOB_FROM_WEB
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    except:
        return

    for file in files:
        fp = os.path.join(UPLOAD_FOLDER, file)
        print(f"\n========== 发现新简历：{file} ==========")

        resume_text = read_resume_text(fp)
        if not resume_text:
            shutil.move(fp, os.path.join(PROCESSED_FOLDER, file))
            continue

        email = extract_email(resume_text)
        print(f"📩 提取邮箱：{email}")

        # 从文件名提取岗位
        job_title = file.split("_")[2]
        matched_jd_content = get_matched_jd_content(job_title)

        # 执行AI评分，传入匹配到的JD内容
        score, report = ai_score_resume_with_jd(resume_text, matched_jd_content, job_title)
        print(f"🎯 AI 打分：{score}")

        mail_status = "失败"
        if email:
            mail_status = send_email(email, report, score, job_title)

        shutil.move(fp, os.path.join(PROCESSED_FOLDER, file))

        # ---------------------- 提取专业/学历/城市 ----------------------
        def extract_major(text):
            match = re.search(r"专业[:：]\s*([^\n\t\r]{2,20})", text)
            return match.group(1).strip() if match else ""

        def extract_education(text):
            edu_list = ["大专", "本科", "硕士", "博士", "研究生", "高中", "中专"]
            for edu in edu_list:
                if edu in text:
                    return edu
            return ""

        def extract_city(text):
            match = re.search(r"(所在城市|现居|城市|地址)[：:]\s*([^\n\t\r]{2,10})", text)
            return match.group(2).strip() if match else ""

        def extract_target_city(text):
            match = re.search(r"(意向城市|期望工作地|意向地点|意向地区)[：:]\s*([^\n\t\r]{2,10})", text)
            return match.group(2).strip() if match else ""

        major = extract_major(resume_text)
        education = extract_education(resume_text)
        city = extract_city(resume_text)
        target_city = extract_target_city(resume_text)

        result_status = "录用" if score >= 85 else "不合适"

        # ---------------------- 9.日志系统（正式版） ----------------------
        try:
            write_recruit_log(
                resume_name=file,
                job_name=job_title,
                score=score,
                email=email if email else "无邮箱",
                mail_status=mail_status,
                result_status=result_status
            )
        except Exception as e:
            print(f"⚠️ 日志写入失败：{e}")
        # ---------------------- 10.详细Excel报表 (保留) ----------------------
        detail_file = "../04_数据文件/recruitment_detail.xlsx"
        detail_data = {
            "投递时间": time.strftime("%Y-%m-%d %H:%M:%S"),
            "岗位": job_title,
            "匹配JD摘要": matched_jd_content[:50] + "...",
            "专业": major,
            "学历": education,
            "所在城市": city,
            "意向地区": target_city,
            "得分": score,
            "邮箱": email if email else "",
            "邮件状态": mail_status,
            "测评结果": result_status
        }

        try:
            if os.path.exists(detail_file):
                df_detail = pd.read_excel(detail_file)
            else:
                df_detail = pd.DataFrame(columns=detail_data.keys())

            df_detail = pd.concat([df_detail, pd.DataFrame([detail_data])], ignore_index=True)
            df_detail.to_excel(detail_file, index=False)
            print("✅ 详细报表已保存至 recruitment_detail.xlsx")
            # 写入MySQL
            save_to_mysql(detail_data)
        except Exception as e:
            print("❌ 详细报表保存失败：", e)
def send_interview_result_email(email, job_name, scores, total, apply_result, all_answers):
    HR_EMAIL = os.getenv("HR_EMAIL")

    # 求职者邮件
    applicant_content = f"""【智聘未来】AI初面结果通知

应聘岗位：{job_name}
面试总分：{total:.1f}/10
录用结果：{apply_result}

各模块得分：
- 基础知识：{scores.get('基础知识',0):.1f}/10
- 项目经历：{scores.get('项目经历',0):.1f}/10
- 实习经历：{scores.get('实习经历',0):.1f}/10
- 技能实战：{scores.get('技能实战',0):.1f}/10
- 技能进阶：{scores.get('技能进阶实战',0):.1f}/10

后续流程将另行邮件通知，请保持邮箱畅通。"""

    # HR邮件
    answers_text = "\n\n".join([
        f"模块[{a['module']}]\nQ: {a['question']}\nA: {a['answer']}" for a in all_answers
    ])
    hr_content = f"""【智聘未来】候选人AI初面报告

求职者邮箱：{email}
应聘岗位：{job_name}
面试总分：{total:.1f}/10
录用建议：{apply_result}

详细得分：
- 基础知识：{scores.get('基础知识',0):.1f}/10 (权重10%)
- 项目经历：{scores.get('项目经历',0):.1f}/10 (权重30%)
- 实习经历：{scores.get('实习经历',0):.1f}/10 (权重30%)
- 技能实战：{scores.get('技能实战',0):.1f}/10 (权重20%)
- 技能进阶：{scores.get('技能进阶实战',0):.1f}/10 (权重10%)

完整问答：
{answers_text}

请登录系统查看详情或进行二次评分。"""

    # 发送求职者邮件
    try:
        msg1 = MIMEMultipart()
        msg1["From"] = MAIL_SENDER
        msg1["To"] = email
        msg1["Subject"] = f"【智聘未来】AI初面结果｜{job_name}｜{apply_result}"
        msg1.attach(MIMEText(applicant_content, "plain", "utf-8"))
        smtp = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtp.login(MAIL_SENDER, MAIL_PASSWORD)
        smtp.sendmail(MAIL_SENDER, email, msg1.as_string())
        smtp.quit()
        print("✅ 求职者面试结果邮件发送成功")
    except Exception as e:
        print(f"❌ 求职者面试结果邮件发送失败: {e}")

    # 发送HR邮件
    if HR_EMAIL:
        try:
            msg2 = MIMEMultipart()
            msg2["From"] = MAIL_SENDER
            msg2["To"] = HR_EMAIL
            msg2["Subject"] = f"【智聘未来】AI初面报告｜{job_name}｜{total:.1f}分｜{apply_result}"
            msg2.attach(MIMEText(hr_content, "plain", "utf-8"))
            smtp2 = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
            smtp2.login(MAIL_SENDER, MAIL_PASSWORD)
            smtp2.sendmail(MAIL_SENDER, HR_EMAIL, msg2.as_string())
            smtp2.quit()
            print("✅ HR面试报告邮件发送成功")
        except Exception as e:
            print(f"❌ HR面试报告邮件发送失败: {e}")
def send_interview_invitation_email(email, candidate_name, interview_url):
    """单独发送面试邀请邮件"""
    HR_EMAIL = os.getenv("HR_EMAIL")

    # 如果没有候选人姓名，用邮箱前缀代替
    if not candidate_name or candidate_name == "未知":
        candidate_name = email.split("@")[0] if email else "同学"

    content = f"""您好{candidate_name}，

由于您的简历初筛达到了我们的标准，现在我们邀请您进行一轮简单的AI面试。

点击下方链接开始面试：
{interview_url}

⏰ 时间限时为48小时，过期不候。
✅ 完成面试后，我们后续会与您继续联系。

祝您面试顺利！

智聘未来 招聘团队"""

    try:
        msg = MIMEMultipart()
        msg["From"] = MAIL_SENDER
        msg["To"] = email
        msg["Subject"] = "【智聘未来】AI初面邀请｜请在48小时内完成"
        msg.attach(MIMEText(content, "plain", "utf-8"))

        smtp = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtp.login(MAIL_SENDER, MAIL_PASSWORD)
        smtp.sendmail(MAIL_SENDER, email, msg.as_string())
        smtp.quit()
        print("✅ 面试邀请邮件发送成功")
        return True
    except Exception as e:
        print(f"❌ 面试邀请邮件发送失败: {e}")
        return False
# # ---------------------- 主程序 ----------------------
# if __name__ == "__main__":
#     print("🤖 AI招聘Agent已启动 (前端指定岗位匹配JD)")
#     print("📌 监听文件夹：", UPLOAD_FOLDER)
#     print("📌 JD库路径：", JD_FOLDER)
#     while True:
#         process_new_files()
#         time.sleep(10)
