"""
提取数据库表结构，拼成给 LLM 看的 Prompt 片段
"""
import sqlite3


def extract_schema(db_path: str) -> str:
    """
    读取 SQLite 数据库，返回表结构描述文本。
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 获取所有表
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    schema_lines = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        col_desc = ", ".join([f"{c[1]} {c[2]}" for c in cols])
        schema_lines.append(f"- {table}({col_desc})")

        # 取 2 行示例数据
        cur.execute(f"SELECT * FROM {table} LIMIT 2")
        sample = cur.fetchall()
        if sample:
            col_names = [c[1] for c in cols]
            for row in sample:
                sample_dict = dict(zip(col_names, row))
                schema_lines.append(f"  示例: {sample_dict}")

    conn.close()

    # 表关系说明
    relations = """
表关系：
- customers.customer_id = orders.customer_id
- products.product_id = orders.product_id
"""
    return "数据库表结构：\n" + "\n".join(schema_lines) + relations
