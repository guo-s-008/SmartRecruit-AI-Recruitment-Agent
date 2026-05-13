# 文件名：format_jd_files.py
# 放在项目根目录运行一次即可
# 功能：规范化 job_jd 文件夹下所有 JD 和评分标准文件的换行格式

import os
import re

JD_DIR = "../04_数据文件/job_jd"

def format_text(text):
    """
    对 JD 或评分标准文本进行 Markdown 友好格式化：
    1. 在常见标题（岗位名称、所属部门等）前插入两个换行
    2. 将编号列表（1. / 2. 等）和分项标题（专业匹配度等）前增加换行
    3. 保留已有换行，但保证段落间有明显间隔
    """
    # 关键标题：前面加双换行
    headers = [
        r'(岗位名称[：:])',
        r'(所属部门[：:])',
        r'(工作地点[：:])',
        r'(薪资范围[：:])',
        r'(岗位职责[：:])',
        r'(任职要求[：:])',
        r'(【评分标准】)',
        r'(专业匹配度)',
        r'(技能匹配度)',
        r'(项目.*?匹配度)',
        r'(学历.*?匹配度)',
        r'(【简历优点】)',
        r'(【简历不足与改进建议】)',
        r'(评分细则[：:])',
    ]
    for header in headers:
        text = re.sub(header, r'\n\n\1', text)

    # 编号列表：1. 2. 等前面加换行（如果前面不是换行）
    text = re.sub(r'(?<!\n)(\d+\.\s)', r'\n\1', text)

    # 将单个换行（非空行）替换为 Markdown 强制换行（两个空格 + 换行）
    # 但保留段落之间的空行（两个连续换行不动）
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            new_lines.append('')  # 保留空行
        else:
            # 非空行：在行尾加两个空格保证 Markdown 换行
            new_lines.append(stripped + '  ')
    formatted = '\n'.join(new_lines)

    # 去除多余的空行（三个以上换行合并为两个）
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    return formatted.strip()


def process_all_files():
    if not os.path.exists(JD_DIR):
        print(f"❌ 目录不存在：{JD_DIR}")
        return

    files = [f for f in os.listdir(JD_DIR) if f.endswith('_jd.txt') or f.endswith('_scoring.txt')]
    if not files:
        print("⚠️ 未找到任何 _jd.txt 或 _scoring.txt 文件")
        return

    for filename in files:
        filepath = os.path.join(JD_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()

        formatted = format_text(raw)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"✅ 已格式化：{filename}")

    print("🎉 全部文件格式化完成，可直接重新运行 import_jd_to_mysql.py 导入数据库")


if __name__ == "__main__":
    process_all_files()