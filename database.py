import sqlite3
from datetime import datetime, timedelta
import os


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
                payment_id TEXT,
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

    def add_pending_payment(self, user_id, tariff, amount, payment_id=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO pending_payments (user_id, tariff, amount, payment_id)
            VALUES (?, ?, ?, ?)
        ''', (user_id, tariff, amount, payment_id))
        self.conn.commit()
        return cursor.lastrowid

    def complete_purchase(self, user_id, tariff, amount, payment_method, vpn_link, days):
        expires_at = datetime.now() + timedelta(days=days)
        self.conn.execute('''
            INSERT INTO purchases (user_id, tariff, amount, payment_method, vpn_link, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, tariff, amount, payment_method, vpn_link, expires_at))

        # Удаляем из ожидающих платежей
        self.conn.execute('DELETE FROM pending_payments WHERE user_id = ? AND tariff = ?',
                          (user_id, tariff))
        self.conn.commit()

    def get_user_purchases(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM purchases 
            WHERE user_id = ?
            ORDER BY purchase_date DESC
        ''', (user_id,))
        return cursor.fetchall()

    def get_pending_payments(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pending_payments ORDER BY created_at DESC')
        return cursor.fetchall()

    def get_payment_by_id(self, payment_id):
        """Получить платеж по ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pending_payments WHERE payment_id = ?', (payment_id,))
        return cursor.fetchone()

    def get_pending_payment_by_user(self, user_id, tariff):
        """Получить ожидающий платеж пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pending_payments WHERE user_id = ? AND tariff = ?',
                      (user_id, tariff))
        return cursor.fetchone()

    def get_all_users(self):
        """Получить всех пользователей (для статистики)"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]

    def remove_pending_payment(self, user_id, tariff):
        """Удалить ожидающий платеж"""
        self.conn.execute('DELETE FROM pending_payments WHERE user_id = ? AND tariff = ?',
                          (user_id, tariff))
        self.conn.commit()