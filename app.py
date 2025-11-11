from flask import Flask
from threading import Thread
from main import bot
import asyncio
import sys
import signal

app = Flask(__name__)

# Запуск бота в отдельном потоке
def run_bot():
    print("🚀 Запускаю Telegram бота...")
    try:
        bot.run()
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")

@app.route('/')
def home():
    return "🤖 VPN Bot is running! | SnowBall VPN"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/health')
def health():
    return "OK"

# Запускаем бот при старте
def start_bot():
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

if __name__ == "__main__":
    start_bot()
    app.run(host='0.0.0.0', port=8080)