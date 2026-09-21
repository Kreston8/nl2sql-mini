"""
Gradio Web 界面 - 5 分钟搞定的可视化操作
启动: python web.py
打开浏览器访问: http://localhost:7860
"""
import gradio as gr
import pandas as pd
from app.schema import extract_schema
from app.sql_gen import generate_sql
from app.executor import execute_sql

DB_PATH = "./data/demo.db"

def do_query(question):
    """处理用户查询，返回 (SQL, 结果表格)"""
    if not question.strip():
        return "请输入问题", None

    # 1. 提取 Schema
    schema = extract_schema(DB_PATH)

    # 2. 生成 SQL
    sql, err = generate_sql(question, schema, DB_PATH)
    if err:
        return f"SQL 生成失败: {err}", None

    # 3. 执行 SQL（失败重试一次）
    rows, exec_err = execute_sql(sql, DB_PATH)
    if exec_err:
        sql, err = generate_sql(question, schema, DB_PATH, error_hint=exec_err)
        if err:
            return f"SQL 重试失败: {err}", None
        rows, exec_err = execute_sql(sql, DB_PATH)
        if exec_err:
            return f"SQL 执行失败: {exec_err}", None

    # 转成 pandas DataFrame（Gradio 渲染最稳定）
    if rows:
        df = pd.DataFrame(rows)
        return sql, df
    return sql, None

# 构建界面
with gr.Blocks(title="Mini NL2SQL") as demo:
    gr.Markdown("# 🗄️ Mini NL2SQL\n用自然语言查数据库，AI 自动生成 SQL")

    with gr.Row():
        question = gr.Textbox(
            label="你的问题",
            placeholder="例如：天津有多少个用户？\n销售额最高的前 5 个商品是什么？\n每个城市的平均订单金额是多少？",
            scale=4,
        )
        btn = gr.Button("查询", variant="primary", scale=1)

    sql_output = gr.Code(label="🤖 生成的 SQL", language="sql")
    result_output = gr.Dataframe(label="📊 查询结果", interactive=False)

    btn.click(do_query, inputs=question, outputs=[sql_output, result_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
