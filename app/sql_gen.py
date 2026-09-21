"""
SQL 生成模块：调 LLM 把自然语言转成 SQL
"""
import os
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY", "your-zhipu-api-key"),
    base_url=os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
)
MODEL = os.getenv("LLM_MODEL", "glm-4.7-flash")

PROMPT_TEMPLATE = """你是 SQLite SQL 专家。根据表结构生成 SQL，只输出 SQL 本身。

表结构：
{schema}

业务规则：销售额统计只算 status='已完成' 的订单。

用户问题：{question}
执行错误（如有）：{error_hint}
SQL："""


def generate_sql(question: str, schema: str, db_path: str, error_hint: str = None) -> tuple:
    """调 LLM 生成 SQL，429 自动重试。返回 (sql, error)"""
    prompt = PROMPT_TEMPLATE.format(
        schema=schema,
        question=question,
        error_hint=error_hint or "无",
    )

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
            )
            sql = resp.choices[0].message.content.strip()
            if sql.startswith("```"):
                sql = sql.split("\n", 1)[1] if "\n" in sql else sql
                sql = sql.replace("```sql", "").replace("```", "").strip()
            if sql.startswith("ERROR:"):
                return None, sql
            if not sql.endswith(";"):
                sql += ";"
            return sql, None
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(2)
                continue
            return None, str(e)

    return None, "重试次数过多"
