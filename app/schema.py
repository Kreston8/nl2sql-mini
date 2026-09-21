"""
提取数据库表结构，拼成给 LLM 看的 Prompt 片段
"""
import sqlite3


def extract_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    lines = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        col_desc = ", ".join([f"{c[1]} {c[2]}" for c in cols])
        lines.append(f"- {table}({col_desc})")

    conn.close()
    return "\n".join(lines)
