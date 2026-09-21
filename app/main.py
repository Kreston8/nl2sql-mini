"""
迷你 NL2SQL 工具 - FastAPI 入口
用户输入自然语言 → 提取 Schema → LLM 生成 SQL → 执行 → 返回结果
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.schema import extract_schema
from app.sql_gen import generate_sql
from app.executor import execute_sql

app = FastAPI(title="Mini NL2SQL", version="0.1.0")

class QueryRequest(BaseModel):
    question: str
    db_path: str = "./data/demo.db"

class QueryResponse(BaseModel):
    question: str
    sql: str
    result: list
    error: str = None

@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """自然语言查询接口"""
    # 1. 提取数据库 Schema
    schema = extract_schema(req.db_path)

    # 2. 调 LLM 生成 SQL（带错误重试）
    sql, err = generate_sql(req.question, schema, req.db_path)
    if err:
        raise HTTPException(status_code=500, detail=f"SQL 生成失败: {err}")

    # 3. 执行 SQL
    rows, exec_err = execute_sql(sql, req.db_path)
    if exec_err:
        # 把错误信息回喂 LLM 重试一次
        sql, err = generate_sql(req.question, schema, req.db_path, error_hint=exec_err)
        if err:
            raise HTTPException(status_code=500, detail=f"SQL 重试仍失败: {err}")
        rows, exec_err = execute_sql(sql, req.db_path)
        if exec_err:
            raise HTTPException(status_code=500, detail=f"SQL 执行失败: {exec_err}")

    return QueryResponse(question=req.question, sql=sql, result=rows)

@app.get("/")
def root():
    return {"msg": "Mini NL2SQL - POST /api/query 用自然语言查数据库"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
