import os
import telebot

BOT_TOKEN = "8825377598:AAHHkGPmb2j4QLFZ0Om054A-dKFN0aLvUtM"
CHANNEL_ID = "@test_furry" 

bot = telebot.TeleBot(BOT_TOKEN)

# Прямая проверка связи
@bot.message_handler(commands=['ping'])
def ping_channel(message):
    try:
        bot.send_message(CHANNEL_ID, "🏓 Живой! Бот на связи!")
        bot.reply_to(message, "✅ Сообщение в канал отправлено!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# Оставляем веб-сервер, чтобы Render не уснул
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Alive")

def run_web_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8080))), WebServer)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    bot.infinity_polling()
