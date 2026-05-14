"""
第2天：LangChain核心概念
=====================

学习目标：
1. 了解LangChain的核心组件
2. 掌握LLM、Prompt、Chain的基本用法
3. 学会如何将LangChain应用到实际项目中
"""

# ------------------- 1. 首先检查是否安装了必要的库 -------------------
import os
import sys

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv 已安装")
except ImportError:
    print("❌ 缺少 python-dotenv，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

try:
    import langchain
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    print("✅ LangChain 相关库已安装")
except ImportError:
    print("❌ 缺少 LangChain 库，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain", "langchain-core"])
    import langchain
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough

# 加载环境变量
load_dotenv("../04_数据文件/.env")

# ------------------- 2. LangChain核心概念讲解 -------------------
print("\n" + "="*80)
print("📚 第2天：LangChain核心概念")
print("="*80)

print("""
一、什么是 LangChain？
----------------------
LangChain 是一个用于开发由语言模型驱动的应用程序的框架。它提供了一套工具和组件，
帮助开发者更容易地构建复杂的 LLM 应用。

核心优势：
1. 组件化：将复杂的 LLM 应用拆分成可复用的组件
2. 链式调用：支持多个组件的串联执行
3. 丰富的集成：与各种 LLM、数据库、工具等集成


二、LangChain 的核心组件
------------------------
1. LLM / Chat Model：语言模型封装
2. Prompt Templates：提示词模板
3. Output Parsers：输出解析器
4. Chains：链（组件的串联）
5. Agents：智能体（具备工具使用能力）
6. Memory：记忆模块
""")

# ------------------- 3. 创建一个兼容阿里云百炼的 LLM 封装 -------------------
import requests
from langchain_core.language_models.llms import LLM
from typing import Any, List, Mapping, Optional

class QwenLLM(LLM):
    """
    自定义的阿里云百炼 Qwen 模型封装
    """
    api_key: str
    api_url: str
    model: str = "qwen-turbo"
    temperature: float = 0.7
    
    @property
    def _llm_type(self) -> str:
        return "qwen-custom"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """调用阿里云百炼 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return f"API返回异常：{data}"
        except Exception as e:
            return f"调用失败：{str(e)}"
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature
        }

# 初始化我们的自定义 LLM
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")

if api_key and api_url:
    llm = QwenLLM(
        api_key=api_key,
        api_url=api_url,
        model="qwen-turbo",
        temperature=0.3
    )
    print("\n✅ 自定义 LLM 初始化成功！")
else:
    print("\n⚠️  请在 .env 文件中配置 API_KEY 和 API_URL")
    sys.exit(1)

# ------------------- 4. 示例1：基础 LLM 调用 -------------------
print("\n" + "-"*80)
print("🎯 示例1：基础 LLM 调用")
print("-"*80)

response = llm.invoke("请用一句话介绍 LangChain")
print(f"\nLLM 回复：{response}")

# ------------------- 5. 示例2：使用 Prompt Template -------------------
print("\n" + "-"*80)
print("🎯 示例2：使用 Prompt Template")
print("-"*80)

# 创建提示词模板
prompt_template = PromptTemplate.from_template(
    "你是一位专业的{role}。请根据以下要求回答：\n\n"
    "要求：{requirement}\n\n"
    "请给出你的回答："
)

# 填充模板
prompt = prompt_template.format(
    role="HR招聘专家",
    requirement="请简述简历评分的3个核心维度"
)

print(f"\n生成的提示词：\n{prompt}")

# 调用 LLM
response2 = llm.invoke(prompt)
print(f"\nLLM 回复：\n{response2}")

# ------------------- 6. 示例3：使用 Chain（LCEL表达式） -------------------
print("\n" + "-"*80)
print("🎯 示例3：使用 Chain（LCEL表达式）")
print("-"*80)

# LCEL：LangChain Expression Language
# 使用 | 操作符将组件串联起来
chain = prompt_template | llm | StrOutputParser()

# 调用链
response3 = chain.invoke({
    "role": "技术面试官",
    "requirement": "请列出Python工程师面试的5个必备知识点"
})

print(f"\nChain 输出：\n{response3}")

# ------------------- 7. 示例4：应用到招聘系统 - 简历评分 -------------------
print("\n" + "-"*80)
print("🎯 示例4：应用到招聘系统 - 简历评分")
print("-"*80)

# 创建简历评分的提示词模板
resume_score_prompt = PromptTemplate.from_template(
    """你是一位专业的HR面试官，请根据【岗位要求】对【简历内容】进行评分。

【岗位名称】：{job_name}
【岗位要求】：{job_requirement}
【简历内容】：{resume_content}

请严格按照以下格式输出：

【评分结果】
总分：XX分（满分100）

【评分理由】
1. 专业匹配度：XX分 - 理由
2. 技能匹配度：XX分 - 理由
3. 项目经验：XX分 - 理由

【综合建议】：简要说明"""
)

# 创建评分链
score_chain = resume_score_prompt | llm | StrOutputParser()

# 测试数据
sample_job_name = "Python后端开发工程师"
sample_job_requirement = """
1. 熟练掌握Python语言，熟悉Django或Flask框架
2. 有MySQL、Redis等数据库使用经验
3. 了解RESTful API设计
4. 有实际项目开发经验优先
"""
sample_resume = """
姓名：张三
学历：本科
专业：计算机科学与技术

技能：
- 熟练使用Python，了解Django框架
- 学习过MySQL数据库
- 了解基本的数据结构和算法

项目经验：
- 课程设计：做过一个简单的学生管理系统
"""

# 调用评分链
print("\n正在进行简历评分...")
score_result = score_chain.invoke({
    "job_name": sample_job_name,
    "job_requirement": sample_job_requirement,
    "resume_content": sample_resume
})

print(f"\n评分结果：\n{score_result}")

# ------------------- 8. 示例5：使用 RunnablePassthrough 进行数据传递 -------------------
print("\n" + "-"*80)
print("🎯 示例5：使用 RunnablePassthrough")
print("-"*80)

from langchain_core.runnables import RunnableParallel

# 并行处理多个任务
parallel_chain = RunnableParallel(
    score_analysis=resume_score_prompt | llm,
    summary=PromptTemplate.from_template(
        "请用50字以内总结这份简历的核心特点：\n{resume_content}"
    ) | llm
)

print("\n正在进行并行处理...")
parallel_result = parallel_chain.invoke({
    "job_name": sample_job_name,
    "job_requirement": sample_job_requirement,
    "resume_content": sample_resume
})

print(f"\n并行处理结果：")
print(f"\n📊 评分分析：\n{parallel_result['score_analysis'][:200]}...")
print(f"\n📝 简历摘要：\n{parallel_result['summary']}")

# ------------------- 9. 总结 -------------------
print("\n" + "="*80)
print("📖 第2天学习总结")
print("="*80)
print("""
今日学习要点：

1. ✅ LangChain 是什么：一个用于构建 LLM 应用的框架
2. ✅ 核心组件：LLM、Prompt Template、Output Parser、Chain
3. ✅ LCEL 表达式：使用 | 操作符串联组件
4. ✅ 实际应用：将 LangChain 应用到简历评分场景

关键知识点：
- PromptTemplate：创建可复用的提示词模板
- LCEL：LangChain Expression Language，优雅的链式调用
- RunnableParallel：并行执行多个任务

明日预告：
- 结构化输出解析器（PydanticOutputParser）
- 对话记忆模块（ConversationMemory）
""")

print("\n🎉 第2天学习完成！")

