"""
初始化 SQLite 数据库：3 张表（customers / products / orders）
运行: python3 init_db.py
"""
import os
import random
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "./data/demo.db"

os.makedirs("./data", exist_ok=True)


def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            city TEXT,
            register_date TEXT
        );
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            price REAL
        );
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            total_amount REAL,
            order_date TEXT,
            status TEXT
        );
    """)

    # 客户数据（100人）
    cities = ["北京", "上海", "广州", "深圳", "杭州",
              "成都", "武汉", "南京", "西安", "重庆", "天津"]
    first_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
                   "勇", "艳", "杰", "涛", "明", "超", "秀", "兰", "霞", "平"]
    last_names = ["张", "王", "李", "赵", "陈", "刘", "杨", "黄", "周", "吴"]

    customers = []
    for i in range(1, 101):
        name = random.choice(last_names) + random.choice(first_names)
        customers.append((
            i,
            name,
            random.choice(["男", "女"]),
            random.randint(18, 65),
            random.choice(cities),
            (datetime.now() - timedelta(days=random.randint(30, 1200))).strftime("%Y-%m-%d"),
        ))
    cur.executemany(
        "INSERT INTO customers VALUES (?,?,?,?,?,?)", customers
    )

    # 商品数据（20种）
    product_list = [
        ("智能手机", "电子产品", 4999), ("笔记本电脑", "电子产品", 6999),
        ("无线耳机", "电子产品", 899), ("机械键盘", "电子产品", 399),
        ("显示器", "电子产品", 1299), ("运动鞋", "服装鞋帽", 599),
        ("羽绒服", "服装鞋帽", 899), ("双肩包", "服装鞋帽", 299),
        ("咖啡机", "家用电器", 1599), ("空气炸锅", "家用电器", 399),
        ("电饭煲", "家用电器", 299), ("洗面奶", "美妆个护", 89),
        ("面膜", "美妆个护", 129), ("保温杯", "日用品", 99),
        ("瑜伽垫", "运动户外", 79), ("篮球", "运动户外", 129),
        ("帐篷", "运动户外", 399), ("办公椅", "家具", 599),
        ("台灯", "家具", 149), ("书架", "家具", 259),
    ]
    products = []
    for i, (name, cat, price) in enumerate(product_list, start=1):
        products.append((i, name, cat, price))
    cur.executemany(
        "INSERT INTO products VALUES (?,?,?,?)", products
    )

    # 订单数据（1000条）
    statuses = ["已完成", "已支付", "已取消", "退款中"]
    orders = []
    for i in range(1, 1001):
        customer_id = random.randint(1, 100)
        product_id = random.randint(1, 20)
        quantity = random.randint(1, 5)
        price = products[product_id - 1][3]
        total = round(price * quantity, 2)
        order_date = (datetime.now() - timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d")
        orders.append((i, customer_id, product_id, quantity, total, order_date, random.choice(statuses)))
    cur.executemany(
        "INSERT INTO orders VALUES (?,?,?,?,?,?,?)", orders
    )

    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH} (customers:100, products:20, orders:1000)")


if __name__ == "__main__":
    init()
