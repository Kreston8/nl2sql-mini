"""
初始化示例数据库：创建一个电商订单表，插入 1000 条测试数据
"""
import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = "./data/demo.db"

def init_db():
    os.makedirs("./data", exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 建表：用户表
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            register_date DATE NOT NULL
        )
    """)

    # 建表：订单表
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            order_date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 插入用户数据
    cities = ["北京", "上海", "天津", "广州", "深圳"]
    for i in range(1, 101):
        name = f"用户{i:03d}"
        city = random.choice(cities)
        reg_date = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).date()
        cursor.execute("INSERT INTO users (name, city, register_date) VALUES (?, ?, ?)",
                       (name, city, reg_date))

    # 插入订单数据
    products = ["笔记本电脑", "手机", "耳机", "键盘", "鼠标", "显示器"]
    statuses = ["已完成", "待发货", "已取消", "退款中"]
    for i in range(1, 1001):
        user_id = random.randint(1, 100)
        product = random.choice(products)
        amount = round(random.uniform(100, 10000), 2)
        status = random.choice(statuses)
        order_date = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 270))).date()
        cursor.execute("INSERT INTO orders (user_id, product_name, amount, status, order_date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, product, amount, status, order_date))

    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH} (users: 100, orders: 1000)")

if __name__ == "__main__":
    init_db()
