import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('vpn_bot.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tariff TEXT,
                amount INTEGER,
                payment_method TEXT,
                vpn_link TEXT,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS pending_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tariff TEXT,
                amount INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, username, first_name):
        self.conn.execute(
            'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
            (user_id, username, first_name)
        )
        self.conn.commit()

    def add_pending_payment(self, user_id, tariff, amount):
        self.conn.execute('''
            INSERT INTO pending_payments (user_id, tariff, amount)
            VALUES (?, ?, ?)
        ''', (user_id, tariff, amount))
        self.conn.commit()

    def get_user_purchases(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM purchases WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

    def get_pending_payments(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pending_payments')
        return cursor.fetchall()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]м