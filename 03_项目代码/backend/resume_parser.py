
"""
简历解析模块
负责简历文件的解析和信息提取
"""
import os
import re
import json
from config import UPLOAD_FOLDER
from utils import (
    read_resume_text,
    extract_email,
    extract_name,
    extract_gender,
    extract_age,
    extract_major,
    extract_education,
    extract_city,
    extract_target_city
)
from ai_scorer import call_llm


def handle_upload_and_parse(file_bytes, filename):
    """
    处理上传的简历文件并解析
    :param file_bytes: 文件字节流
    :param filename: 文件名
    :return: 解析结果字典
    """
    temp_dir = UPLOAD_FOLDER
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"_parse_{filename}")
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    text = read_resume_text(temp_path)
    email = extract_email(text)

    name = extract_name(text)
    gender = extract_gender(text)
    age = extract_age(text)
    major = extract_major(text)
    education = extract_education(text)
    city = extract_city(text)

    if not name or not gender or not age:
        try:
            prompt = f"""从以下简历文本中提取姓名、性别、年龄。
如果文本中没有相关信息，返回空字符串。
只返回JSON：{{"name":"...","gender":"...","age":"..."}}

简历文本：
{text[:800]}"""
            content = call_llm([{"role": "user", "content": prompt}], temperature=0.0)
            info = json.loads(content)
            name = name or info.get("name", "")
            gender = gender or info.get("gender", "")
            age = age or info.get("age", "")
        except:
            pass

    try:
        os.remove(temp_path)
    except:
        pass

    return {
        "text": text,
        "email": email,
        "name": name,
        "gender": gender,
        "age": age,
        "major": major,
        "education": education,
        "city": city,
        "target_city": ""
    }


def extract_info_from_resume_text(text):
    """
    从简历文本中提取所有信息
    :param text: 简历文本
    :return: 信息字典
    """
    return {
        "text": text,
        "email": extract_email(text),
        "name": extract_name(text),
        "gender": extract_gender(text),
        "age": extract_age(text),
        "major": extract_major(text),
        "education": extract_education(text),
        "city": extract_city(text),
        "target_city": extract_target_city(text)
    }

