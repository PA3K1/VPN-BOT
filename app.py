from flask import Flask
import os
import subprocess
import threading

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

# Запуск бота в отдельном процессе
def run_bot():
    print("🚀 Starting Telegram Bot in separate process...")
    try:
        subprocess.run(["python", "-c", """
from main import bot
print('🤖 Bot starting...')
bot.run()
print('🤖 Bot stopped')
        """], check=True)
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем веб-сервер
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Web server starting on port {port}")
    app.run(host='0.0.0.0', port=port)