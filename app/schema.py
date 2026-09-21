"""
Schema 提取模块：从 SQLite 数据库提取表结构，拼成 Prompt 上下文
"""
import sqlite3

def extract_schema(db_path: str) -> str:
    """提取所有表的建表语句，拼成 Prompt 上下文"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        # 获取建表语句
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
        create_sql = cursor.fetchone()[0]
        schema_parts.append(f"表 {table} 的结构：\n{create_sql};")

        # 获取前 3 行示例数据（帮助 LLM 理解业务含义）
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        if rows:
            sample = "示例数据：\n"
            sample += "  列: " + ", ".join(cols) + "\n"
            for r in rows:
                sample += "  行: " + str(r) + "\n"
            schema_parts.append(sample)

    conn.close()
    return "\n\n".join(schema_parts)
