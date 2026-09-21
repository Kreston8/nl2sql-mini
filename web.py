"""
Gradio Web 界面 - NL2SQL 智能查询
启动: python3 web.py
浏览器: http://localhost:7860
"""
import gradio as gr
import pandas as pd
from app.schema import extract_schema
from app.sql_gen import generate_sql
from app.executor import execute_sql

DB_PATH = "./data/demo.db"


def do_query(question):
    """
    自然语言 -> SQL -> 执行 -> 返回 (SQL, 结果DataFrame, 状态)
    """
    if not question.strip():
        return "", pd.DataFrame(), "请输入问题"

    schema = extract_schema(DB_PATH)
    sql, err = generate_sql(question, schema, DB_PATH)
    if err:
        return "", pd.DataFrame(), f"SQL 生成失败: {err}"

    rows, exec_err = execute_sql(sql, DB_PATH)
    if exec_err:
        # 带错误提示重试一次
        sql, err = generate_sql(question, schema, DB_PATH, error_hint=exec_err)
        if err:
            return sql, pd.DataFrame(), f"SQL 重试失败: {err}"
        rows, exec_err = execute_sql(sql, DB_PATH)
        if exec_err:
            return sql, pd.DataFrame(), f"SQL 执行失败: {exec_err}"

    df = pd.DataFrame(rows) if rows else pd.DataFrame()
    return sql, df, f"查询成功，共 {len(df)} 行"


examples = [
    ["查询所有客户数量"],
    ["统计每个城市的客户数量，按数量从高到低排序"],
    ["查询销售额最高的前10个商品"],
    ["统计每种商品分类的销售总额"],
    ["查询购买总金额最高的前10名客户"],
    ["查询年龄大于30岁的女性客户"],
    ["统计每个月的订单数量"],
]

with gr.Blocks(
    title="Mini NL2SQL",
) as demo:
    gr.Markdown(
        """
        # 🗄️ Mini NL2SQL
        输入中文自然语言，AI 自动生成 SQLite SQL 并执行查询。
        """
    )

    question = gr.Textbox(
        label="你的问题",
        placeholder="例如：统计每个城市的客户数量",
        lines=1,
    )

    submit_btn = gr.Button("生成 SQL 并执行", variant="primary")

    gr.Examples(
        examples=examples,
        inputs=question,
        label="示例问题（点一下快速填充）",
    )

    sql_output = gr.Code(label="🤖 生成的 SQL", language="sql")
    result_output = gr.Dataframe(label="📊 查询结果", interactive=False)
    status_output = gr.Textbox(label="执行状态", interactive=False)

    submit_btn.click(
        do_query,
        inputs=question,
        outputs=[sql_output, result_output, status_output],
    )
    question.submit(
        do_query,
        inputs=question,
        outputs=[sql_output, result_output, status_output],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
