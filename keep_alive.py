from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "VPN Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()