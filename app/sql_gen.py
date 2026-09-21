"""
SQL 生成模块：调 LLM 把自然语言转成 SQL
支持 OpenAI 兼容 API（DeepSeek/通义千问/OpenAI 均可）
"""
import os
from openai import OpenAI

# 从环境变量读 API key（用户自己配置）
# 默认用智谱 GLM（兼容 OpenAI 格式）
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY", "your-zhipu-api-key"),
    base_url=os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
)
MODEL = os.getenv("LLM_MODEL", "glm-4.7-flash")

PROMPT_TEMPLATE = """你是一个 SQL 生成专家。根据下面的数据库表结构和用户问题，生成一条可执行的 SQLite SQL 语句。

要求：
1. 只输出 SQL 语句本身，不要任何解释或 markdown 代码块标记
2. SQL 必须兼容 SQLite 语法
3. 不要生成 DROP/DELETE/UPDATE 等修改数据的语句，只生成 SELECT 查询
4. 如果问题无法用 SQL 回答，输出: ERROR: 无法回答

数据库表结构：
{schema}

用户问题：{question}

之前执行错误提示（如果有）：{error_hint}

SQL："""

def generate_sql(question: str, schema: str, db_path: str, error_hint: str = None) -> tuple:
    """
    调 LLM 生成 SQL
    返回 (sql, error) 元组，成功时 error 为 None
    """
    prompt = PROMPT_TEMPLATE.format(
        schema=schema,
        question=question,
        error_hint=error_hint or "无"
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # 低温度保证 SQL 稳定
            max_tokens=500,
        )
        sql = resp.choices[0].message.content.strip()

        # 清理可能的 markdown 代码块标记
        if sql.startswith("```"):
            sql = sql.split("\n", 1)[1] if "\n" in sql else sql.replace("```sql", "").replace("```", "")
            sql = sql.replace("```", "").strip()

        if sql.startswith("ERROR:"):
            return None, sql

        return sql, None

    except Exception as e:
        return None, str(e)
