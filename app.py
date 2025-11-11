from flask import Flask
from threading import Thread
import os
import asyncio
from pyrogram import Client
import config

app = Flask(__name__)

# Создаем клиент бота
bot = Client(
    "vpn_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Запускаем бота в основном потоке
def run_bot():
    print("🚀 Запускаю Telegram бота...")
    bot.run()

@app.route('/')
def home():
    return "🤖 VPN Bot is running! | SnowBall VPN"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/health')
def health():
    return "OK"

# Запускаем Flask и бота
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask
    print("🌐 Web server starting on port 10000")
    app.run(host='0.0.0.0', port=10000, debug=False)