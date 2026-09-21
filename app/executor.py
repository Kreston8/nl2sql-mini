"""
SQL 执行器：只读执行，带安全校验
"""
import sqlite3
import pandas as pd

FORBIDDEN_KEYWORDS = [
    "insert ", "update ", "delete ", "drop ", "alter ",
    "create ", "replace ", "attach ", "detach ", "pragma ", "vacuum ",
]


def validate_sql(sql: str):
    """
    只读 SQL 安全检查。
    如果有多条语句，自动截断到第一条。
    """
    normalized = sql.strip().lower()
    if not (normalized.startswith("select") or normalized.startswith("with")):
        raise ValueError("只允许执行 SELECT 或 WITH 查询")

    for kw in FORBIDDEN_KEYWORDS:
        if kw in normalized:
            raise ValueError(f"检测到禁止操作: {kw.strip()}")

    # 如果有多条 SQL（分号分隔），只取第一条
    sql = sql.strip()
    if ";" in sql:
        first_stmt = sql.split(";", 1)[0].strip()
        if not first_stmt.endswith(";"):
            first_stmt += ";"
        return first_stmt

    if not sql.endswith(";"):
        sql += ";"
    return sql


def execute_sql(sql: str, db_path: str):
    """
    以只读模式执行 SQL，返回 (rows, error)。
    rows 是 list[dict] 格式。
    """
    try:
        sql = validate_sql(sql)
    except ValueError as e:
        return None, str(e)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA query_only = ON")  # 只读模式
    try:
        df = pd.read_sql_query(sql, conn)
        if len(df) > 1000:
            df = df.head(1000)
        rows = df.to_dict("records")
        return rows, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()
