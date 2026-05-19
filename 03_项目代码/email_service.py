
"""
邮件服务模块
负责发送各类通知邮件
"""
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG, LOG_ROOT
from utils import summarize_text


def send_email(receive_email, score, job_title, apply_result, report="", advantage="", shortcoming=""):
    """
    发送简历评分邮件（求职者和HR双端）
    :param receive_email: 求职者邮箱
    :param score: 分数
    :param job_title: 岗位名称
    :param apply_result: 录用结果（录用/不合适）
    :param report: 完整报告（求职者用）
    :param advantage: 优势（HR用）
    :param shortcoming: 不足（HR用）
    :return: 邮件状态（成功/失败）
    """
    HR_EMAIL = EMAIL_CONFIG.get("hr_email")
    mail_status = "失败"

    if apply_result == "录用":
        hr_tip = f"请您联系求职者邮箱：{receive_email}，尽快安排后续面试。"
    else:
        hr_tip = "该候选人已为您录入企业人才库，可后续持续关注。"

    advantage_text = advantage if advantage else "无明显优势信息"
    shortcoming_text = shortcoming if shortcoming else "无明显短板信息"

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

    print("\n" + "=" * 80)
    print("📄 求职者邮件全文：")
    print("=" * 80)
    print(applicant_content)
    print("\n" + "=" * 80)
    print("📄 HR邮件全文：")
    print("=" * 80)
    print(hr_content)
    print("=" * 80 + "\n")

    log_dir = os.path.join(LOG_ROOT, "log_eminfo")
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

{'=' * 60}
"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content)
    print(f"📝 邮件内容已保存至日志：{log_file}")

    try:
        if not receive_email:
            print("❌ 错误：简历中未提取到邮箱，无法发送")
            return mail_status

        msg1 = MIMEMultipart()
        msg1["From"] = EMAIL_CONFIG["sender"]
        msg1["To"] = receive_email
        msg1["Subject"] = "【智聘未来】你的简历测评结果"
        msg1.attach(MIMEText(applicant_content, "plain", "utf-8"))
        smtp = smtplib.SMTP_SSL(EMAIL_CONFIG["server"], EMAIL_CONFIG["port"])
        smtp.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
        smtp.sendmail(EMAIL_CONFIG["sender"], receive_email, msg1.as_string())
        smtp.quit()
        print("✅ 求职者邮件发送成功")

        if HR_EMAIL:
            msg2 = MIMEMultipart()
            msg2["From"] = EMAIL_CONFIG["sender"]
            msg2["To"] = HR_EMAIL
            msg2["Subject"] = f"【智聘未来】简历投递通知｜得分：{score}｜{apply_result}"
            msg2.attach(MIMEText(hr_content, "plain", "utf-8"))
            smtp2 = smtplib.SMTP_SSL(EMAIL_CONFIG["server"], EMAIL_CONFIG["port"])
            smtp2.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            smtp2.sendmail(EMAIL_CONFIG["sender"], HR_EMAIL, msg2.as_string())
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


def send_interview_result_email(email, job_name, scores, total, apply_result, all_answers):
    """
    发送面试结果邮件
    :param email: 求职者邮箱
    :param job_name: 岗位名称
    :param scores: 各模块分数
    :param total: 总分
    :param apply_result: 录用结果
    :param all_answers: 所有答案
    """
    HR_EMAIL = EMAIL_CONFIG.get("hr_email")

    applicant_content = f"""【智聘未来】AI初面结果通知

应聘岗位：{job_name}
面试总分：{total:.1f}/10
录用结果：{apply_result}

各模块得分：
- 基础知识：{scores.get('基础知识', 0):.1f}/10
- 项目经历：{scores.get('项目经历', 0):.1f}/10
- 实习经历：{scores.get('实习经历', 0):.1f}/10
- 技能实战：{scores.get('技能实战', 0):.1f}/10
- 技能进阶：{scores.get('技能进阶实战', 0):.1f}/10

后续流程将另行邮件通知，请保持邮箱畅通。"""

    answers_text = "\n\n".join(
        [f"模块[{a['module']}]\nQ: {a['question']}\nA: {a['answer']}" for a in all_answers]
    )
    hr_content = f"""【智聘未来】候选人AI初面报告

求职者邮箱：{email}
应聘岗位：{job_name}
面试总分：{total:.1f}/10
录用建议：{apply_result}

详细得分：
- 基础知识：{scores.get('基础知识', 0):.1f}/10 (权重10%)
- 项目经历：{scores.get('项目经历', 0):.1f}/10 (权重30%)
- 实习经历：{scores.get('实习经历', 0):.1f}/10 (权重30%)
- 技能实战：{scores.get('技能实战', 0):.1f}/10 (权重20%)
- 技能进阶：{scores.get('技能进阶实战', 0):.1f}/10 (权重10%)

完整问答：
{answers_text}

请登录系统查看详情或进行二次评分。"""

    try:
        msg1 = MIMEMultipart()
        msg1["From"] = EMAIL_CONFIG["sender"]
        msg1["To"] = email
        msg1["Subject"] = f"【智聘未来】AI初面结果｜{job_name}｜{apply_result}"
        msg1.attach(MIMEText(applicant_content, "plain", "utf-8"))
        smtp = smtplib.SMTP_SSL(EMAIL_CONFIG["server"], EMAIL_CONFIG["port"])
        smtp.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
        smtp.sendmail(EMAIL_CONFIG["sender"], email, msg1.as_string())
        smtp.quit()
        print("✅ 求职者面试结果邮件发送成功")
    except Exception as e:
        print(f"❌ 求职者面试结果邮件发送失败: {e}")

    if HR_EMAIL:
        try:
            msg2 = MIMEMultipart()
            msg2["From"] = EMAIL_CONFIG["sender"]
            msg2["To"] = HR_EMAIL
            msg2["Subject"] = f"【智聘未来】AI初面报告｜{job_name}｜{total:.1f}分｜{apply_result}"
            msg2.attach(MIMEText(hr_content, "plain", "utf-8"))
            smtp2 = smtplib.SMTP_SSL(EMAIL_CONFIG["server"], EMAIL_CONFIG["port"])
            smtp2.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            smtp2.sendmail(EMAIL_CONFIG["sender"], HR_EMAIL, msg2.as_string())
            smtp2.quit()
            print("✅ HR面试报告邮件发送成功")
        except Exception as e:
            print(f"❌ HR面试报告邮件发送失败: {e}")


def send_interview_invitation_email(email, candidate_name, interview_url):
    """
    发送面试邀请邮件
    :param email: 求职者邮箱
    :param candidate_name: 候选人姓名
    :param interview_url: 面试链接
    :return: 是否成功
    """
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
        msg["From"] = EMAIL_CONFIG["sender"]
        msg["To"] = email
        msg["Subject"] = "【智聘未来】AI初面邀请｜请在48小时内完成"
        msg.attach(MIMEText(content, "plain", "utf-8"))

        smtp = smtplib.SMTP_SSL(EMAIL_CONFIG["server"], EMAIL_CONFIG["port"])
        smtp.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
        smtp.sendmail(EMAIL_CONFIG["sender"], email, msg.as_string())
        smtp.quit()
        print("✅ 面试邀请邮件发送成功")
        return True
    except Exception as e:
        print(f"❌ 面试邀请邮件发送失败: {e}")
        return False


def handle_send_email(receive_email, score, job_title, apply_result, report="", advantage="", shortcoming=""):
    """
    封装的发送邮件接口（供外部调用），包含摘要精简
    :param receive_email: 求职者邮箱
    :param score: 分数
    :param job_title: 岗位名称
    :param apply_result: 录用结果
    :param report: 完整报告
    :param advantage: 优势
    :param shortcoming: 不足
    :return: 邮件状态
    """
    short_adv = summarize_text(advantage, 100) if advantage else ""
    short_short = summarize_text(shortcoming, 100) if shortcoming else ""
    return send_email(receive_email, score, job_title, apply_result, report, short_adv, short_short)

