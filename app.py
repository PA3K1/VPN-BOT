from flask import Flask
import os
import threading
from main import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ VPN Telegram Bot is Running!"

@app.route('/health')
def health():
    return "🟢 Bot is Healthy"

@app.route('/ping')
def ping():
    return "pong"

# Запуск бота в отдельном потоке
def run_bot():
    print("🚀 Starting Telegram Bot...")
    bot.run()

if __name__ == "__main__":
    # Запускаем бота в фоне
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем веб-сервер на порту из переменной окружения
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port)