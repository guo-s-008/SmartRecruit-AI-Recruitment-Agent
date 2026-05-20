
"""
Excel 操作模块
负责 Excel 文件的读写操作
"""
import os
import pandas as pd
from datetime import datetime
from config import EXCEL_DATA_PATH


def handle_save_to_excel(detail_data):
    """
    保存数据到 Excel
    :param detail_data: 详细数据字典
    """
    excel_path = EXCEL_DATA_PATH
    today_str = datetime.now().strftime("%Y-%m-%d")

    row = {
        "ID": detail_data.get("ID", ""),
        "投递时间": detail_data.get("投递时间", ""),
        "姓名": detail_data.get("姓名", ""),
        "性别": detail_data.get("性别", ""),
        "年龄": detail_data.get("年龄", ""),
        "学历": detail_data.get("学历", ""),
        "投递岗位": detail_data.get("岗位", ""),
        "所在城市": detail_data.get("所在城市", ""),
        "意向城市": detail_data.get("意向地区", ""),
        "简历得分": detail_data.get("得分", 0),
        "是否通过初筛": "是" if detail_data.get("测评结果") == "录用" else "否",
        "是否进行AI面试": "",
        "基础知识得分": "",
        "项目经历得分": "",
        "实习经历得分": "",
        "技能实战得分": "",
        "进阶实战得分": "",
        "总分": "",
        "是否录用": ""
    }

    df_new = pd.DataFrame([row])
    for col in ["是否进行AI面试", "是否录用", "基础知识得分", "项目经历得分", "实习经历得分", "技能实战得分", "进阶实战得分", "总分"]:
        df_new[col] = df_new[col].astype(str)

    try:
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        if os.path.exists(excel_path):
            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                if today_str in writer.sheets:
                    df_old = pd.read_excel(excel_path, sheet_name=today_str)
                    for col in df_new.columns:
                        if col in df_old.columns and df_new[col].dtype == object:
                            df_old[col] = df_old[col].astype(str)
                    df_combined = pd.concat([df_old, df_new], ignore_index=True)
                    df_combined.to_excel(writer, sheet_name=today_str, index=False)
                else:
                    df_new.to_excel(writer, sheet_name=today_str, index=False)
        else:
            df_new.to_excel(excel_path, sheet_name=today_str, index=False)
        print(f"✅ 数据已写入 Excel：{excel_path} → Sheet: {today_str}")
    except Exception as e:
        import traceback
        print(f"❌ Excel 写入失败: {e}")
        traceback.print_exc()


def update_excel_interview_scores(record_id, scores, total, apply_result):
    """
    更新 Excel 中的面试分数
    :param record_id: 记录ID
    :param scores: 各模块分数
    :param total: 总分
    :param apply_result: 录用结果
    """
    excel_path = EXCEL_DATA_PATH
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"🔔 开始更新 Excel 面试分数，ID={record_id}, Sheet={today_str}", flush=True)

    try:
        if not os.path.exists(excel_path):
            print(f"❌ Excel 文件不存在：{excel_path}")
            return

        df = pd.read_excel(excel_path, sheet_name=today_str)
        df["ID_str"] = df["ID"].astype(str)
        mask = df["ID_str"] == str(record_id)
        print(f"🔍 查找 ID={record_id}，匹配行数：{mask.sum()}", flush=True)

        if mask.any():
            idx = df[mask].index[0]

            for col in ["是否进行AI面试", "是否录用", "基础知识得分", "项目经历得分", "实习经历得分", "技能实战得分", "进阶实战得分", "总分"]:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            df.at[idx, "是否进行AI面试"] = "是"
            df.at[idx, "基础知识得分"] = str(scores.get("基础知识", 0))
            df.at[idx, "项目经历得分"] = str(scores.get("项目经历", 0))
            df.at[idx, "实习经历得分"] = str(scores.get("实习经历", 0))
            df.at[idx, "技能实战得分"] = str(scores.get("技能实战", 0))
            df.at[idx, "进阶实战得分"] = str(scores.get("技能进阶实战", 0))
            df.at[idx, "总分"] = str(total)
            df.at[idx, "是否录用"] = apply_result

            df.drop(columns=["ID_str"], inplace=True)

            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=today_str, index=False)
            print(f"✅ Excel 面试分数已更新，ID={record_id}", flush=True)
        else:
            print(f"⚠️ 未在 Excel 中找到 ID={record_id}，请检查 Excel 中的 ID 列与传入值", flush=True)
    except Exception as e:
        import traceback
        print(f"❌ 更新 Excel 面试得分失败: {e}")
        traceback.print_exc()

