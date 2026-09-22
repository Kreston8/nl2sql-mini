"""
SQL 生成模块：调 LLM 把自然语言转成 SQL
"""
import os
import re
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY", "your-zhipu-api-key"),
    base_url=os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
)
MODEL = os.getenv("LLM_MODEL", "glm-4-flash")

PROMPT_TEMPLATE = """你是 SQLite SQL 专家。根据表结构生成 SELECT 查询语句，只输出 SQL 本身，不要 markdown 代码块。

表结构：
{schema}

表关系：
- customers.customer_id = orders.customer_id
- products.product_id = orders.product_id

业务规则：
- 销售额统计只算 status='已完成' 的订单
- 查询明细加 LIMIT 1000

用户问题：{question}
执行错误（如有）：{error_hint}
SQL："""


def clean_sql(text: str) -> str:
    """从 LLM 输出中提取纯 SQL 语句"""
    text = text.strip()

    # 去掉 markdown 代码块
    text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    text = text.strip()

    # 如果不是以 SELECT/WITH 开头，找一下
    if not re.match(r"^(SELECT|WITH)", text, re.IGNORECASE):
        match = re.search(r"(SELECT|WITH)\b", text, re.IGNORECASE)
        if match:
            text = text[match.start():].strip()

    # 只保留第一条 SQL
    if ";" in text:
        text = text.split(";", 1)[0].strip()

    if not text.endswith(";"):
        text += ";"

    return text


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
            raw = resp.choices[0].message.content.strip()

            if raw.startswith("ERROR:"):
                return None, raw

            sql = clean_sql(raw)
            return sql, None

        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(2)
                continue
            return None, str(e)

    return None, "重试次数过多"
