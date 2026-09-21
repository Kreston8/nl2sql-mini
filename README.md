# Mini NL2SQL - 基于 LLM 的数据库自然语言查询工具

## 项目简介

一个 500 行代码的迷你 NL2SQL 工具：用户输入自然语言 → 自动提取数据库 Schema → 调 LLM 生成 SQL → 执行返回结果。

**技术栈**：Python + FastAPI + SQLite + OpenAI 兼容 API（DeepSeek/通义千问均可）

## 快速开始

### 1. 安装依赖

```bash
cd /root/projects/nl2sql-mini
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 用 DeepSeek（推荐，便宜）
export LLM_API_KEY="sk-your-deepseek-key"
export LLM_BASE_URL="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"
```

### 3. 初始化示例数据库

```bash
python init_db.py
```

### 4. 启动服务

```bash
cd app
uvicorn main:app --reload --port 8000
```

### 5. 测试

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "天津有多少个用户？"}'
```

## 项目结构

```
nl2sql-mini/
├── app/
│   ├── main.py       # FastAPI 入口
│   ├── schema.py     # 提取 SQLite 表结构 → Prompt 上下文
│   ├── sql_gen.py    # 调 LLM 生成 SQL + 错误重试
│   └── executor.py   # 执行 SQL（安全检查只允许 SELECT）
├── data/
│   └── demo.db       # SQLite 示例数据库（init_db.py 生成）
├── init_db.py        # 初始化示例数据
├── requirements.txt
└── README.md
```

## 核心流程（面试必讲）

```
用户提问
  ↓
1. schema.py 提取数据库表结构（建表语句 + 前 3 行示例数据）
  ↓
2. sql_gen.py 把 Schema + 用户问题拼成 Prompt → 调 LLM 生成 SQL
  ↓
3. executor.py 执行 SQL（安全检查只允许 SELECT）
  ↓
4. 如果执行报错 → 把错误信息回喂 LLM 重试一次
  ↓
返回 JSON 结果
```

## 面试话术

**"介绍一下这个项目？"**

> "这是一个迷你 NL2SQL 工具，500 行代码。用户输入自然语言，系统自动提取 SQLite 的表结构和示例数据，拼成 Prompt 调 LLM 生成 SQL，然后执行返回结果。如果 SQL 执行报错，会把错误信息回喂给 LLM 重试一次。
>
> 技术难点是 Schema Linking——表太多全塞进 Prompt 超长，所以我在 schema.py 里做了示例数据提取，把前 3 行数据也拼进 Prompt，LLM 理解业务含义更准。"

**"为什么选这个方案？"**

> "之前看过 DB-GPT，但它太重量级了，几万行代码，一个人根本学不透。我就自己用 FastAPI 写了个最简版，核心就是 4 个模块：Schema 提取、Prompt 拼接、SQL 生成、SQL 执行。代码量小，每一行都能讲清楚。"

## 自定义扩展

- 把 SQLite 换成 PostgreSQL/MySQL：改 executor.py 的连接部分
- 加 RAG：把历史 SQL 向量化，检索相似示例拼进 Prompt（这就是 DB-GPT 的做法）
- 加 Web 前端：用 Gradio 5 分钟搞定一个聊天界面
