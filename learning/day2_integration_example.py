"""
第2天：LangChain 与招聘系统集成示例
=================================

这个文件展示如何将 LangChain 应用到你现有的招聘系统中
对比原有方式和 LangChain 方式的区别
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
env_path = "../04_数据文件/.env"
if os.path.exists(env_path):
    load_dotenv(env_path)

print("\n" + "="*80)
print("🔧 LangChain 与招聘系统集成示例")
print("="*80)

# ------------------- 第一部分：原有方式 vs LangChain 方式 -------------------
print("\n" + "-"*80)
print("📊 对比：原有方式 vs LangChain 方式")
print("-"*80)

print("""
原有方式（你的现有代码）：
------------------------
1. 直接使用 requests.post() 调用 API
2. 手动拼接提示词字符串
3. 手动处理返回结果
4. 代码分散，复用性差
""")

print("""
LangChain 方式：
----------------
1. 组件化设计，职责清晰
2. PromptTemplate 管理提示词
3. LCEL 链式调用，代码优雅
4. 易于维护和扩展
""")

# ------------------- 第二部分：创建兼容的 LLM 封装 -------------------
print("\n" + "-"*80)
print("🔨 步骤1：创建兼容阿里云百炼的 LLM 封装")
print("-"*80)

import requests
from typing import Any, List, Mapping, Optional
from langchain_core.language_models.llms import LLM

class RecruitmentLLM(LLM):
    """
    招聘系统专用的 LLM 封装
    兼容阿里云百炼 API，也支持模拟模式
    """
    api_key: str = ""
    api_url: str = ""
    model: str = "qwen-turbo"
    temperature: float = 0.3
    use_mock: bool = True
    
    @property
    def _llm_type(self) -> str:
        return "recruitment-llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        if self.use_mock:
            return self._mock_response(prompt)
        
        # 真实 API 调用（与你的 agent.py 中的 call_llm 类似）
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
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return f"API异常：{data}"
        except Exception as e:
            return f"调用失败：{str(e)}"
    
    def _mock_response(self, prompt: str) -> str:
        """模拟回复"""
        import time
        time.sleep(0.3)
        if "简历" in prompt and "评分" in prompt:
            return """【简历评分】
分数：78
【分项评分标准】
1. 专业匹配度：25分
2. 技能匹配度：22分
3. 项目经验匹配度：20分
4. 综合素养：11分
【简历优势】
- 专业对口，计算机相关专业
- 掌握 Python 和基础数据库知识
【简历不足与改进建议】
- 缺少实际商业项目经验
- 建议补充 Django/Flask 框架学习"""
        elif "面试" in prompt and "题目" in prompt:
            return "1. 请介绍一下你的项目经验？\n2. Python 的装饰器是什么？\n3. 如何优化数据库查询？"
        else:
            return "这是模拟的 LLM 回复内容。"
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "temperature": self.temperature}

print("✅ RecruitmentLLM 类创建完成")

# 初始化 LLM
api_key = os.getenv("API_KEY", "")
api_url = os.getenv("API_URL", "")
use_mock = not (api_key and api_url and api_key != "your_api_key_here")

llm = RecruitmentLLM(
    api_key=api_key,
    api_url=api_url,
    use_mock=use_mock
)
print(f"✅ LLM 初始化完成（模拟模式：{use_mock}）")

# ------------------- 第三部分：使用 LangChain 重构简历评分 -------------------
print("\n" + "-"*80)
print("🔨 步骤2：使用 LangChain 重构简历评分功能")
print("-"*80)

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建简历评分提示词模板
resume_score_prompt = PromptTemplate.from_template(
    """你是专业HR面试官，根据【岗位JD】对简历进行严格评分（满分100）。

【岗位名称】
{job_name}

【岗位JD要求】
{jd_content}

【简历内容】
{resume_text}

请严格按以下格式输出：

【简历评分】
分数：{{分数}}

【分项评分标准】
1. 专业匹配度：{{分数}}分
2. 技能匹配度：{{分数}}分
3. 项目经验匹配度：{{分数}}分
4. 综合素养：{{分数}}分

【简历优势】
{{优势内容}}

【简历不足与改进建议】
{{建议内容}}
"""
)

# 创建评分链
score_chain = resume_score_prompt | llm | StrOutputParser()

print("✅ 简历评分链创建完成")

# 测试评分功能
print("\n📝 测试简历评分功能...")

# 读取一个真实的 JD 示例
sample_jd_path = "../04_数据文件/job_jd/数据分析师_jd.txt"
if os.path.exists(sample_jd_path):
    with open(sample_jd_path, "r", encoding="utf-8") as f:
        sample_jd = f.read()
else:
    sample_jd = """岗位：数据分析师
要求：
1. 熟悉 SQL 和 Python
2. 有数据分析经验
3. 了解统计学基础"""

sample_resume = """姓名：李明
学历：本科
专业：统计学
技能：Python, SQL, Excel
项目经验：做过课程设计的数据分析作业"""

result = score_chain.invoke({
    "job_name": "数据分析师",
    "jd_content": sample_jd,
    "resume_text": sample_resume
})

print("\n📊 评分结果：")
print(result[:300] + "..." if len(result) > 300 else result)

# ------------------- 第四部分：创建面试题目生成链 -------------------
print("\n" + "-"*80)
print("🔨 步骤3：创建面试题目生成链")
print("-"*80)

interview_prompt = PromptTemplate.from_template(
    """你是资深技术面试官，请根据以下信息生成面试题目。

【岗位】：{job_name}
【简历】：{resume_text}
【JD要求】：{jd_content}

请生成5个面试题目，涵盖技术基础、项目经验、技能实战等方面。
每个题目请说明考察点。"""
)

interview_chain = interview_prompt | llm | StrOutputParser()

print("✅ 面试题目生成链创建完成")

print("\n📝 测试面试题目生成...")
interview_result = interview_chain.invoke({
    "job_name": "数据分析师",
    "resume_text": sample_resume,
    "jd_content": sample_jd
})

print("\n❓ 面试题目：")
print(interview_result[:300] + "..." if len(interview_result) > 300 else interview_result)

# ------------------- 第五部分：并行处理示例 -------------------
print("\n" + "-"*80)
print("🔨 步骤4：使用 RunnableParallel 并行处理")
print("-"*80)

from langchain_core.runnables import RunnableParallel

# 同时进行评分和生成面试题
parallel_chain = RunnableParallel(
    score=score_chain,
    interview_questions=interview_chain
)

print("✅ 并行处理链创建完成")

print("\n⚡ 执行并行处理...")
parallel_result = parallel_chain.invoke({
    "job_name": "数据分析师",
    "jd_content": sample_jd,
    "resume_text": sample_resume
})

print(f"\n📊 并行处理完成！")
print(f"   - 评分结果长度：{len(parallel_result['score'])}")
print(f"   - 面试题长度：{len(parallel_result['interview_questions'])}")

# ------------------- 第六部分：创建可复用的服务类 -------------------
print("\n" + "-"*80)
print("🔨 步骤5：创建可复用的 RecruitmentService 类")
print("-"*80)

class RecruitmentService:
    """
    招聘系统核心服务类
    封装所有 LangChain 相关功能
    """
    
    def __init__(self, llm):
        self.llm = llm
        self._init_chains()
    
    def _init_chains(self):
        """初始化所有链"""
        # 简历评分链
        self.score_prompt = PromptTemplate.from_template(
            """你是专业HR面试官，根据【岗位JD】对简历进行评分。
【岗位名称】：{job_name}
【岗位JD】：{jd_content}
【简历内容】：{resume_text}
请输出评分结果。"""
        )
        self.score_chain = self.score_prompt | self.llm | StrOutputParser()
        
        # 面试题生成链
        self.interview_prompt = PromptTemplate.from_template(
            """你是面试官，请根据简历和JD生成面试题。
【岗位】：{job_name}
【简历】：{resume_text}
请生成5个面试题。"""
        )
        self.interview_chain = self.interview_prompt | self.llm | StrOutputParser()
    
    def score_resume(self, job_name, jd_content, resume_text):
        """简历评分"""
        return self.score_chain.invoke({
            "job_name": job_name,
            "jd_content": jd_content,
            "resume_text": resume_text
        })
    
    def generate_interview_questions(self, job_name, resume_text):
        """生成面试题"""
        return self.interview_chain.invoke({
            "job_name": job_name,
            "resume_text": resume_text
        })
    
    def process_resume(self, job_name, jd_content, resume_text):
        """完整处理流程：评分 + 生成面试题"""
        parallel_chain = RunnableParallel(
            score=self.score_chain,
            interview_questions=self.interview_chain
        )
        return parallel_chain.invoke({
            "job_name": job_name,
            "jd_content": jd_content,
            "resume_text": resume_text
        })

print("✅ RecruitmentService 类创建完成")

# 测试服务类
print("\n🔧 测试 RecruitmentService...")
service = RecruitmentService(llm)
result = service.process_resume(
    job_name="数据分析师",
    jd_content=sample_jd,
    resume_text=sample_resume
)
print("✅ 服务调用成功！")

# ------------------- 第七部分：总结与迁移建议 -------------------
print("\n" + "="*80)
print("📋 迁移建议总结")
print("="*80)

print("""
如何将 LangChain 集成到你的现有系统：
----------------------------------------

1. 创建 langchain_service.py 文件
   - 放置 RecruitmentLLM 类
   - 放置 RecruitmentService 类

2. 修改 agent_service.py
   - 导入 RecruitmentService
   - 替换原有的 call_llm 调用

3. 优点：
   - 代码更清晰，职责分离
   - 提示词集中管理
   - 便于添加新功能
   - 为后续的记忆、Agent、RAG 做准备

4. 文件结构建议：
   /workspace/03_项目代码/
   ├── agent.py              (保持不变)
   ├── agent_service.py      (修改，使用 LangChain)
   ├── langchain_service.py  (新增，LangChain 封装)
   └── ...
""")

print("\n🎉 集成示例完成！")
print(f"📁 示例文件位置：{os.path.abspath(__file__)}")

