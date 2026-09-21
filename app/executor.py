"""
SQL 执行模块：在 SQLite 上执行查询 SQL，返回结果
"""
import sqlite3

def execute_sql(sql: str, db_path: str) -> tuple:
    """
    执行 SELECT 查询 SQL
    返回 (rows, error) 元组
    """
    # 安全检查：只允许 SELECT
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return None, "只允许 SELECT 查询语句"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        conn.close()

        # 转成字典列表方便 JSON 序列化
        result = [dict(zip(cols, row)) for row in rows]
        return result, None

    except Exception as e:
        return None, str(e)
